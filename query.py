import sys
import pprint
from googleapiclient.discovery import build


def augment():
    #TODO do augment here
    return None

def main():
    api_key = sys.argv[1]
    engine_id = sys.argv[2]
    precision = sys.argv[3]
    query = sys.argv[4].lower()

    service = build("customsearch", "v1", developerKey=api_key)
    resp = service.cse().list(q=query, cx=engine_id).execute()
    # pprint.pprint(resp)
    items = resp['items']
    rel = 0
    while rel < float(precision):
        count = 0
        rel = 0

        print("Parameters: ", api_key, engine_id, precision)
        print("API key      = " + api_key)
        print("Engine Key   = " + engine_id)
        print("Precision    = " + precision)
        print("Query        = " + query)
        print("Google Search Results:")
        print("========================")

        for i, item in enumerate(items):
            print("Result " + str(i+1))
            print("Title: ", item.get('title'))
            print("Link: ", item.get('link'))
            print("Description: ", item.get('snippet'))
            feedback = input("Relevant? (Y/N)")
            if feedback == "Y":
                count += 1
        rel = count / 10

        print("========================")
        print("FEEDBACK SUMMARY")
        print("Query: " + query)
        print("Precision: " + str(rel) + " < " + str(precision))
        # TODO step 4
        augment()
        print("Augmented by ...")



if __name__ == '__main__':
    sys.exit(main())
