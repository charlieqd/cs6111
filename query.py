import sys
import requests
from googleapiclient.discovery import build


def main():
    api_key = sys.argv[1]
    engine_id = sys.argv[2]
    precision = sys.argv[3]
    query = sys.argv[4].lower()

    print("parameters are ", api_key, engine_id, precision)
    print(query)

    service = build("customsearch", "v1", developerKey=api_key)
    resp = service.cse().list(q=query, cx=engine_id).execute()
    items = resp['items']
    for item in items:
        print(item)
        break
        print(item.get('title'))
        print(item.get('link'))
        print(item.get('description'))


if __name__ == '__main__':
    sys.exit(main())
