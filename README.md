# utils
Small utils for working with TOPlist

## api2csv.py
Python3 util without any external dependecies (not even requests) to download statistics from TOPlist API and convert them to CSV

Usage:
 * Variables are for simplicity hardcoded to source. Edit `API_TOKEN` and `POST_DATA` in code.
 * Run `python3 api2csv.py` for output to stdout or `python3 api2csv.py output-prefix` to export results to file(s). Multiple files are created when multiple `stats` in `POST_DATA` config where specified.
