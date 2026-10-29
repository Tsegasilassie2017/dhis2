import unittest
from unittest.mock import Mock

from dhis_quality import Client, check_values


class QualityTests(unittest.TestCase):
    def test_zero_duplicate_and_negative(self):
        row = dict(orgUnit='unit', period='201801', dataElement='count', value='0')
        negative = dict(row, value='-1', orgUnit='other')
        issues = check_values([row, row.copy(), negative], {'count': {'valueType': 'INTEGER_ZERO_OR_POSITIVE'}})
        self.assertEqual([i['issue'] for i in issues], ['duplicate_value', 'outside_metadata_range'])

    def test_numeric_validation(self):
        rows = [dict(dataElement='count', value=v, orgUnit=str(i))
                for i, v in enumerate(['NaN', 'abc', '1.5', ''])]
        self.assertEqual([i['issue'] for i in check_values(rows, {'count': {'valueType': 'INTEGER'}})],
                         ['invalid_numeric_value', 'invalid_numeric_value', 'non_integer_value', 'blank_value'])

    def test_https_required(self):
        for url in ['http://example.org', 'https://user:pass@example.org', 'https://example.org?token=x']:
            with self.assertRaises(ValueError):
                Client(url, 'user', 'pass')

    def test_request_authentication_and_query(self):
        client = Client('https://example.org', 'user', 'password')
        response = Mock()
        response.headers = {'Content-Type': 'application/json'}
        response.read.return_value = b'{"dataValues": []}'
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        client.opener = Mock()
        client.opener.open.return_value = response
        self.assertEqual(client.get('dataValueSets.json', period='201801'), {'dataValues': []})
        request = client.opener.open.call_args.args[0]
        self.assertEqual(request.get_method(), 'GET')
        self.assertIn('period=201801', request.full_url)
        self.assertTrue(request.get_header('Authorization').startswith('Basic '))


if __name__ == '__main__':
    unittest.main()
