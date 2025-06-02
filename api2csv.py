import csv
import urllib.request
import urllib.error
import json
import sys

API_URL = "https://profi.toplist.cz/api/v1/stat/process"  # API endpoint
API_TOKEN = ""  # API key from https://profi.toplist.cz/#server_setting
POST_DATA = {
    "date": "2025-05-30",
    "interval": "day",
    "step": "hour",
    "stats": ["visits", "totalPages"], # "kw" values from https://profi.toplist.cz/api/sharedData/job
    "rowLimit": 100
}    # Replace with your POST data if needed

def fetch_data():
    data = json.dumps(POST_DATA).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if API_TOKEN:
        req.add_header("serverKey", API_TOKEN)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}", file=sys.stderr)
        try:
            body = e.read().decode()
            print("Response body:", body, file=sys.stderr)
        except Exception:
            pass
        sys.exit(1)

def write_csv(data, fileobj):
    if not data:
        print("No data to write.", file=sys.stderr)
        return
    writer = csv.DictWriter(fileobj, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

def __table_to_csv(table):
    keys = tuple(x['keyword'] for x in table['keys'])

    cvs_data = []
    for row in table['data']:
        row_data = {}
        for (index, value) in enumerate(row):
            row_data[keys[index]] = value
        cvs_data.append(row_data)
    return cvs_data

def main():
    """Response example:
        "{'dateFrom': '2025-05-30', 'dateTo': '2025-05-30', 'filters': [], 'rowLimit': 100, 'statResults': {'pageView': {'dataSets': {'pageview': {'data': [146, 124, 76, 61, 73, 207, 275, 414, 577, 577, 525, 521, 536, 583, 376, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'title': 'zhlédnutí'}}, 'title': 'zhlédnutí', 'titleShort': 'zhlédnutí'}, 'visits': {'dataSets': {'visits': {'data': [66, 42, 40, 38, 39, 68, 111, 138, 171, 176, 178, 161, 173, 159, 120, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'title': 'návštěvy'}}, 'title': 'počet návštěv', 'titleShort': 'návštěvy', 'axeY': 'návštěvy'}}, 'stats': ['visits', 'pageView'], 'stepId': 'hour', 'timeline': ['2025-05-30T00:00:00', '2025-05-30T01:00:00', '2025-05-30T02:00:00', '2025-05-30T03:00:00', '2025-05-30T04:00:00', '2025-05-30T05:00:00', '2025-05-30T06:00:00', '2025-05-30T07:00:00', '2025-05-30T08:00:00', '2025-05-30T09:00:00', '2025-05-30T10:00:00', '2025-05-30T11:00:00', '2025-05-30T12:00:00', '2025-05-30T13:00:00', '2025-05-30T14:00:00', '2025-05-30T15:00:00', '2025-05-30T16:00:00', '2025-05-30T17:00:00', '2025-05-30T18:00:00', '2025-05-30T19:00:00', '2025-05-30T20:00:00', '2025-05-30T21:00:00', '2025-05-30T22:00:00', '2025-05-30T23:00:00'], 'toplistId': 1, 'type': 'profi', 'uuid': '5324eae9c02148778908056386f1fa3b'}",done,5324eae9c02148778908056386f1fa3b
    """

    data = fetch_data()['data']
    for stat in data['stats']:
        cvs_data = []
        if 'table' in data['statResults'][stat]['dataSets']:
            cvs_data = __table_to_csv(data['statResults'][stat]['dataSets']['table'])
        else:
            i = 0
            for time in data['timeline']:
                row = {'timeline': time}
                for dataset in data['statResults'][stat]['dataSets']:
                    row[stat+':'+dataset] = data['statResults'][stat]['dataSets'][dataset]['data'][i]
                cvs_data.append(row)
                i += 1
        if len(sys.argv) > 1:
            filename = f"{sys.argv[1]}-{stat}.csv"
            with open(filename, "w", newline='', encoding="utf-8") as csvfile:
                write_csv(cvs_data, csvfile)
            print(f"Data exported to {filename}")
        else:
            write_csv(cvs_data, sys.stdout)

if __name__ == "__main__":
    main()
