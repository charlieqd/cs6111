import sys
import pprint
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
    # pprint.pprint(resp)
    items = resp['items']
    for item in items:
        print("Title: ", item.get('title'))
        print("Link: ", item.get('link'))
        print("Description: ", item.get('snippet'))


if __name__ == '__main__':
    sys.exit(main())
