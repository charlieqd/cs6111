import sys
import pprint
from googleapiclient.discovery import build
from sklearn.feature_extraction.text import CountVectorizer

def augment(query, items):
    R = []
    IR = []
    for doc in items:
        if doc["relevant"]:
            R.append[doc]
        else:
            IR.append[doc]
    
    return None

def main():
    api_key = sys.argv[1]
    engine_id = sys.argv[2]
    precision = sys.argv[3]
    query = sys.argv[4]

    service = build("customsearch", "v1", developerKey=api_key)
    resp = service.cse().list(q=query, cx=engine_id).execute()
    # pprint.pprint(resp)
    items = resp['items']
    rel = -1
    while rel < float(precision) and rel != 0:
        count = 0
        rel = 0
        length = 10

        print("Parameters: ", api_key, engine_id, precision)
        print("API key      = " + api_key)
        print("Engine Key   = " + engine_id)
        print("Precision    = " + precision)
        print("Query        = " + query)
        print("Google Search Results:")
        print("========================")

        for i, item in enumerate(items):
            if not item.get('mime') or item['mime'] != 'text/html':
                print("Result " + str(i+1) + " is not html snippet, skip")
                length -= 1
                continue
            
            print("Result " + str(i+1))
            print("Title: ", item.get('title'))
            print("Link: ", item.get('link'))
            print("Description: ", item.get('snippet'))
            feedback = input("Relevant? (Y/N)")
            if feedback == "Y":
                item["relevant"] = True
                count += 1
            else:
                item["relevant"] = False

        print("========================")
        print("FEEDBACK SUMMARY")
        print("Query: " + query)
        if length == 0:
            print("No valid html results!")
            break

        rel = count / length
        if rel == 0:
            print("Precision: 0")
            print("Stopped")
        elif rel < precision:
            print("Precision: " + str(rel) + " < " + str(precision))
            # TODO step 4
            augment(query, items)
            print("Augmented by ...")
        else:
            print("Precision: " + rel)
            print("Desired precision reached, done")



if __name__ == '__main__':
    sys.exit(main())
