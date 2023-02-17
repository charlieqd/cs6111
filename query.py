import sys
import pprint
import random
from googleapiclient.discovery import build
from sklearn.feature_extraction.text import CountVectorizer

stop_words = ('the', 'a', 'an', 'in', 'of',
              'to', 'and', 'as', 'at', 'be',
              'for', 'from', 'is', 'it', 'on',
              'was', 'were', 'with')

# levenshtein edit distance in wikipedia
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def augment(query, items):
    queries = query.split(' ')
    R = []
    IR = []
    beta = 0.85
    gamma = 0.15
    p1 = random.random()
    p2 = random.random()

    for doc in items:
        if doc["relevant"]:
            R.append(doc['title'] + ' ' + doc['snippet'])
        else:
            IR.append(doc['title'] + ' ' + doc['snippet'])

    vectorizer = CountVectorizer()
    R_vectors = vectorizer.fit_transform(R).toarray()
    R_terms = vectorizer.get_feature_names()
    R_freq = {}

    IR_vectors = vectorizer.fit_transform(IR).toarray()
    IR_terms = vectorizer.get_feature_names()

    for i, vector in enumerate(R_vectors):
        # get vector for each relevant search result
        print("Relevant document vector", i)
        for j, freq in enumerate(vector):
            term = R_terms[j]
            skip = False

            # check stop words
            if term in stop_words:
                continue

            # check edit distance
            for q in queries:
                if levenshtein(term, q) <= 1:
                    skip = True
                    break
            if skip:
                continue
            
            # check frequencies
            if freq == 0:
                continue

            # modified rocchio's algorithm
            if term in IR_terms and p2 < beta:
                continue

            print(term, ":", freq)
            if term in R_freq:
                R_freq[term] += freq
            else:
                R_freq[term] = 1

    print(R_freq)
    #TODO construct new query
    return query

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
            if 'mime' in item and item['mime'] != 'text/html':
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
        elif rel < float(precision):
            print("Precision: " + str(rel) + " < " + str(precision))
            query = augment(query, items)
            print("Augmented by " + query)
        else:
            print("Precision: " + rel)
            print("Desired precision reached, done")



if __name__ == '__main__':
    sys.exit(main())
