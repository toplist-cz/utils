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
