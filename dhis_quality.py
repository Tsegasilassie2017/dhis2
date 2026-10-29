#!/usr/bin/env python3
"""Read-only DHIS2 aggregate report fetcher. Python 3.10+, no dependencies."""
import argparse
import base64
import csv
import getpass
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None  # Never forward the Authorization header to another URL.


class Client:
    def __init__(self, base, username, password):
        parsed = urlsplit(base)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('Use an HTTPS server base URL without credentials, query, or fragment.')
        self.base = base.rstrip('/')
        self.authorization = 'Basic ' + base64.b64encode(f'{username}:{password}'.encode()).decode()
        self.opener = build_opener(NoRedirect())

    def get(self, endpoint, **params):
        request = Request(self.base + '/api/' + endpoint + '?' + urlencode(params),
                          headers={'Authorization': self.authorization, 'Accept': 'application/json'})
        try:
            with self.opener.open(request, timeout=90) as response:
                if 'json' not in response.headers.get('Content-Type', ''):
                    raise ValueError('Server returned a non-JSON response; check the base URL and API access.')
                return json.load(response)
        except HTTPError as error:
            raise ValueError(f'DHIS2 returned HTTP {error.code}; check credentials, permissions, and network settings.') from None
        except URLError:
            raise ValueError('Could not reach DHIS2 securely; check network access and certificate trust.') from None

    def collection(self, endpoint, key, **params):
        result = self.get(endpoint, paging='false', **params)
        if key not in result or not isinstance(result[key], list):
            raise ValueError(f'Unexpected response from {endpoint}.')
        return result[key]


def choose(items, label):
    if not items:
        raise ValueError(f'No accessible {label} found.')
    for index, item in enumerate(items, 1):
        print(f"{index}. {item.get('displayName', item['id'])} [{item['id']}]")
    while True:
        answer = input(f'Select {label} number: ').strip()
        if answer.isdigit() and 1 <= int(answer) <= len(items):
            return items[int(answer) - 1]
        print('Enter one of the listed numbers.')


NUMERIC = {'NUMBER', 'UNIT_INTERVAL', 'PERCENTAGE', 'INTEGER', 'INTEGER_POSITIVE',
           'INTEGER_NEGATIVE', 'INTEGER_ZERO_OR_POSITIVE'}


def check_values(values, elements):
    """Flag only violations implied by DHIS2 metadata; zero is a reported value."""
    from decimal import Decimal, InvalidOperation
    issues, seen = [], set()
    for row in values:
        key = tuple(row.get(k, '') for k in ('orgUnit', 'period', 'dataElement', 'categoryOptionCombo', 'attributeOptionCombo'))
        def flag(code):
            issues.append(dict(zip(('orgUnit', 'period', 'dataElement', 'categoryOptionCombo', 'attributeOptionCombo'), key), issue=code, value=row.get('value', '')))
        if key in seen:
            flag('duplicate_value')
        seen.add(key)
        value = row.get('value')
        if value is None or str(value).strip() == '':
            flag('blank_value')
            continue
        kind = elements.get(row.get('dataElement'), {}).get('valueType')
        if kind not in NUMERIC:
            continue
        try:
            number = Decimal(str(value))
            if not number.is_finite():
                raise InvalidOperation
        except InvalidOperation:
            flag('invalid_numeric_value')
            continue
        if kind.startswith('INTEGER') and number != number.to_integral_value():
            flag('non_integer_value')
        if ((kind == 'INTEGER_POSITIVE' and number <= 0) or
            (kind == 'INTEGER_NEGATIVE' and number >= 0) or
            (kind == 'INTEGER_ZERO_OR_POSITIVE' and number < 0) or
            (kind == 'UNIT_INTERVAL' and not 0 <= number <= 1) or
            (kind == 'PERCENTAGE' and not 0 <= number <= 100)):
            flag('outside_metadata_range')
    return issues


def write_csv(path, rows, fields):
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='https://dhis.moh.gov.et')
    parser.add_argument('--search', default='Lemi')
    parser.add_argument('--output', default='reports')
    args = parser.parse_args()
    os.umask(0o077)
    username = getpass.getpass('DHIS2 username (hidden): ')
    password = getpass.getpass('DHIS2 password (hidden): ')
    client = Client(args.url, username, password)
    del password, username
    client.get('me.json', fields='id')
    info = client.get('system/info.json')
    print('Server calendar:', info.get('calendar', 'not supplied by server'))
    print('Confirm the API period in DHIS2. Do not assume Meskerem 2018 equals Gregorian September.')
    period = input('Exact DHIS2 monthly period ID (YYYYMM): ').strip()
    if not re.fullmatch(r'\d{4}(0[1-9]|1[0-2])', period):
        raise ValueError('Expected a monthly API period ID YYYYMM.')
    org = choose(client.collection('organisationUnits.json', 'organisationUnits',
                 filter='displayName:ilike:' + args.search, fields='id,displayName,path'), 'organisation unit')
    units = client.collection('organisationUnits.json', 'organisationUnits',
                              filter='path:like:' + org['id'], fields='id,displayName')
    unit_ids = {unit['id'] for unit in units} | {org['id']}
    datasets = client.collection('dataSets.json', 'dataSets',
                                fields='id,displayName,periodType,organisationUnits[id]')
    datasets = [d for d in datasets if d.get('periodType') == 'Monthly' and
                any(u['id'] in unit_ids for u in d.get('organisationUnits', []))]
    dataset = choose(datasets, 'monthly dataset')
    metadata = client.get('dataSets/' + dataset['id'] + '.json',
                          fields='id,displayName,dataSetElements[dataElement[id,displayName,valueType]]')
    elements = {e['dataElement']['id']: e['dataElement'] for e in metadata.get('dataSetElements', [])}
    result = client.get('dataValueSets.json', dataSet=dataset['id'], period=period,
                        orgUnit=org['id'], children='true')
    if 'dataValues' not in result or not isinstance(result['dataValues'], list):
        raise ValueError('Unexpected data value response; no report written.')
    values = result['dataValues']
    if any(r.get('period') != period or r.get('orgUnit') not in unit_ids for r in values):
        raise ValueError('Response contains values outside the selected scope; no report written.')
    issues = check_values(values, elements)
    assigned = {u['id'] for u in dataset['organisationUnits']} & unit_ids
    reported = {r['orgUnit'] for r in values if str(r.get('value', '')).strip()}
    coverage = [{'orgUnit': uid, 'has_values': uid in reported} for uid in sorted(assigned)]
    output = Path(args.output) / f"{dataset['id']}_{org['id']}_{period}"
    output.mkdir(parents=True, exist_ok=False)
    (output / 'aggregate_data.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    write_csv(output / 'issues.csv', issues, ['orgUnit', 'period', 'dataElement', 'categoryOptionCombo', 'attributeOptionCombo', 'issue', 'value'])
    write_csv(output / 'coverage.csv', coverage, ['orgUnit', 'has_values'])
    summary = {'organisationUnit': org, 'dataset': dataset, 'period': period,
               'serverCalendar': info.get('calendar'), 'valueCount': len(values), 'issueCount': len(issues),
               'assignedUnitsWithoutValues': len(assigned - reported),
               'limitations': ['Coverage means presence of values, not official submission completeness.',
                               'Timeliness, validation-rule consistency, and historical outliers are not checked.',
                               'Absent individual values are not automatically errors; optional fields and zero suppression may apply.']}
    (output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Saved {len(values)} values and {len(issues)} flagged issues to {output}.')
    print('See summary.json for scope and checks not performed.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print('\nCancelled.', file=sys.stderr)
        sys.exit(130)
