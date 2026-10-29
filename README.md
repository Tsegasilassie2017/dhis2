# DHIS2 monthly report quality tool

Requires Python 3.10 or later; no packages to install.

```sh
cd /workspace/dhis2
python dhis_quality.py
```

Run in an interactive terminal you control. Both username and password are hidden
at the prompts; do not send them in chat. The tool uses HTTPS Basic authentication,
keeps credentials in process memory, rejects redirects, and makes only GET requests.
Your account must have permission to read the selected aggregate reports and metadata.
SSO-only accounts may require an administrator-supported API authentication method.

Select the exact API period, Lemi Kura organisation unit, and monthly dataset when
prompted. Meskerem 2018 is an Ethiopian calendar label: verify the actual period ID
in your DHIS2 installation before entering it. The tool prints the server calendar
when supplied. It does not guess a conversion.

Outputs are private local files under `reports/`: aggregate data, issues CSV,
coverage CSV, and a summary recording scope and limitations. Existing output folders
are preserved. Use `--output OTHER_DIRECTORY` for another run. Keep health reporting
outputs out of public repositories.

Checks cover duplicate records, blank returned values, invalid numbers, integer
constraints, metadata-defined ranges, and assigned facilities with no values.
Zero is valid. Coverage is not official reporting completeness. Timeliness,
cross-indicator validation rules, and historical outliers are not yet implemented.
No issues does not establish that a report is fully correct.

The cloud environment must allow `dhis.moh.gov.et`. A saved network draft must be
applied through environment settings before cloud fetching can work. This tool's
interactive login does not require the previously declared API-token secret.

```sh
python -m unittest discover -s tests -v
```
