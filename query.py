import sys
import pprint
import random
from googleapiclient.discovery import build
from sklearn.feature_extraction.text import CountVectorizer
from collections import defaultdict

# ToDo: use another stop words dict
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
            insertions = previous_row[
                             j + 1] + 1  # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1  # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def augment(query, items):
    R = []
    IR = []
    beta = 0.85  # beta for relevant docs
    gamma = 0.15  # gamma for irrelevant docs

    for doc in items:
        if doc["relevant"]:
            R.append(doc['title'] + ' ' + doc['snippet'])
        else:
            IR.append(doc['title'] + ' ' + doc['snippet'])

    print("R is ")
    for r in R:
        print(r)
    cv = CountVectorizer(stop_words='english')
    cv_fit = cv.fit_transform(R)
    word_list = cv.get_feature_names()
    count_list = cv_fit.toarray().sum(axis=0)
    r_term_dict = dict(zip(word_list, count_list))
    print("r_term_dict is ")
    print(r_term_dict)
    r_term_count, ir_term_count = 0, 0
    for t, v in r_term_dict.items():
        r_term_count += v
    cv_fit = cv.fit_transform(IR)
    ir_word_list = cv.get_feature_names()
    ir_count_list = cv_fit.toarray().sum(axis=0)
    ir_term_dict = dict(zip(ir_word_list, ir_count_list))
    print("ir_term_dict is ")
    print(ir_term_dict)
    for t, v in ir_term_dict.items():
        ir_term_count += v
    term_to_value = defaultdict(int)

    # Rocchio's Algorithm + query words ordering
    for term, freq in r_term_dict.items():
        term_to_value[term] += freq * beta / r_term_count
    for term, freq in ir_term_dict.items():
        term_to_value[term] -= freq * gamma / ir_term_count
    sortedTerm = sorted(term_to_value.items(), key=lambda x: x[1], reverse=True)
    print("Sorted Term is ")
    print(sortedTerm)

    queries = query.split(' ')
    n_query = []
    q_counter = 2
    for i in range(len(sortedTerm)):
        if sortedTerm[i][0] not in queries:
            n_query.append(sortedTerm[i][0])
            q_counter -= 1
            if q_counter < 1:
                break
    term_to_new_value = defaultdict(int)
    for word in n_query:
        term_to_new_value[word] = term_to_value[word]

    sortedTermNew = dict(sorted(term_to_new_value.items(), key=lambda x: x[1], reverse=True))

    requery = ' '.join(queries + list(sortedTermNew.keys()))
    print("requery is ", requery)

    # R_vectors = vectorizer.fit_transform(R).toarray()
    # print("R_vectors aree: ")
    # print(R_vectors)
    # R_terms = vectorizer.get_feature_names()
    # print(R_terms)
    # R_freq = {}
    #
    # IR_vectors = vectorizer.fit_transform(IR).toarray()
    # IR_terms = vectorizer.get_feature_names()
    #
    # for i, vector in enumerate(R_vectors):
    #     # get vector for each relevant search result
    #     print("Relevant document vector", i)
    #     for j, freq in enumerate(vector):
    #         term = R_terms[j]
    #         skip = False
    #
    #         # check stop words
    #         if term in stop_words:
    #             continue
    #
    #         # check edit distance
    #         for q in queries:
    #             if levenshtein(term, q) <= 1:
    #                 skip = True
    #                 break
    #         if skip:
    #             continue
    #
    #         # check frequencies
    #         if freq == 0:
    #             continue
    #
    #         # modified rocchio's algorithm
    #         if term in IR_terms and p2 < gamma:
    #             continue
    #
    #         print(term, ":", freq)
    #         if term in R_freq:
    #             R_freq[term] += freq
    #         else:
    #             R_freq[term] = 1
    #
    # print(R_freq)
    # TODO construct new query
    return requery


def main():
    api_key = sys.argv[1]
    engine_id = sys.argv[2]
    precision = sys.argv[3]
    query = sys.argv[4]

    service = build("customsearch", "v1", developerKey=api_key)
    rel = -1
    result = []
    while rel < float(precision) and rel != 0:
        resp = service.cse().list(q=query, cx=engine_id).execute()
        items = resp['items']
        count, length = 0, 10

        print("Parameters: ", api_key, engine_id, precision)
        print("API key      = " + api_key)
        print("Engine Key   = " + engine_id)
        print("Precision    = " + precision)
        print("Query        = " + query)
        print("Google Search Results:")
        print("========================")
        result = []
        for i, item in enumerate(items):
            if 'mime' in item and item['mime'] != 'text/html':
                print("Result " + str(i + 1) + " is not html snippet, skip")
                length -= 1
                continue

            print("Result " + str(i + 1))
            print("Title: ", item.get('title'))
            print("Link: ", item.get('link'))
            print("Description: ", item.get('snippet'))
            feedback = input("Relevant? (Y/N)")
            if feedback == "Y" or feedback == "y":
                item["relevant"] = True
                result.append(item)
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
            break
        elif rel < float(precision):
            print("Precision: " + str(rel) + " < " + str(precision))
            query = augment(query, items)
            print("Augmented by " + query)
        else:
            print("Precision: " + str(rel))
            print("Desired precision reached, done")
            break
    print("========================")
    if rel >= float(precision):
        print("Final Results are ")
        for i in range(len(result)):
            print("Result " + str(i + 1))
            print("Title: ", item.get('title'))
            print("Link: ", item.get('link'))
            print("Description: ", item.get('snippet'))


if __name__ == '__main__':
    sys.exit(main())
