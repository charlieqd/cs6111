import sys
from googleapiclient.discovery import build
from sklearn.feature_extraction.text import CountVectorizer
from collections import defaultdict


def read_words(filename):
    f = open(filename, "r")
    words = f.read().split()
    f.close()
    return words


def log_transcript(logs):
    with open("transcript.txt", "a") as f:
        f.write(logs + "\n")
    print(logs)


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

    # Get the word list for relevant documents
    cv = CountVectorizer(stop_words=read_words("stop_words.txt"))
    cv_fit = cv.fit_transform(R)
    word_list = cv.get_feature_names_out()
    count_list = cv_fit.toarray().sum(axis=0)
    # Generate a dict: word -> frequency in relevant documents
    r_term_dict = dict(zip(word_list, count_list))
    r_term_count, ir_term_count = 0, 0
    for t, v in r_term_dict.items():
        r_term_count += v

    # Get the word list for relevant documents
    cv_fit = cv.fit_transform(IR)
    ir_word_list = cv.get_feature_names_out()
    ir_count_list = cv_fit.toarray().sum(axis=0)
    # Generate a dict: word -> frequency in irrelevant documents
    ir_term_dict = dict(zip(ir_word_list, ir_count_list))
    for t, v in ir_term_dict.items():
        ir_term_count += v

    # Rocchio's Algorithm + query words ordering
    term_to_value = defaultdict(int)
    for term, freq in r_term_dict.items():
        term_to_value[term] += freq * beta / r_term_count
    for term, freq in ir_term_dict.items():
        term_to_value[term] -= freq * gamma / ir_term_count
    # Sort the words by the value calculated by Rocchio's Algorithm
    sortedTerm = sorted(term_to_value.items(), key=lambda x: x[1], reverse=True)

    queries = query.split(' ')
    n_query = []
    # Pick up two new words
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

    # Order new words
    sortedTermNew = dict(sorted(term_to_new_value.items(), key=lambda x: x[1], reverse=True))

    # Generate new query
    requery = ' '.join(queries + list(sortedTermNew.keys()))
    print("requery is ", requery)

    return requery


def main():
    api_key = sys.argv[1]
    engine_id = sys.argv[2]
    precision = sys.argv[3]
    query = sys.argv[4]

    service = build("customsearch", "v1", developerKey=api_key)
    rel = -1
    while rel < float(precision) and rel != 0:
        resp = service.cse().list(q=query, cx=engine_id, fileType="html").execute()
        items = resp['items']
        count, length = 0, 10

        log_transcript("Parameters: ")
        log_transcript("API key      = " + api_key)
        log_transcript("Engine Key   = " + engine_id)
        log_transcript("Precision    = " + precision)
        log_transcript("Query        = " + query)
        log_transcript("Google Search Results:")
        log_transcript("========================")
        for i, item in enumerate(items):
            if 'mime' in item and item['mime'] != 'text/html':
                log_transcript("Result " + str(i + 1) + " is not html snippet, skip")
                length -= 1
                continue

            log_transcript("Result " + str(i + 1))
            log_transcript("Title: " + item.get('title'))
            log_transcript("Link: " + item.get('link'))
            log_transcript("Description: " + item.get('snippet'))
            feedback = input("Relevant? (Y/N)")
            if feedback == "Y" or feedback == "y":
                item["relevant"] = True
                count += 1
            else:
                item["relevant"] = False

        log_transcript("========================")
        log_transcript("FEEDBACK SUMMARY")
        log_transcript("Query: " + query)
        if length == 0:
            log_transcript("No valid html results!")
            break

        rel = count / length
        if rel == 0:
            log_transcript("Precision: 0")
            log_transcript("Stopped")
            break
        elif rel < float(precision):
            log_transcript("Precision: " + str(rel) + " < " + str(precision))
            query = augment(query, items)
            log_transcript("Augmented by " + query)
        else:
            log_transcript("Precision: " + str(rel))
            log_transcript("Desired precision reached, done")
            break
    log_transcript("========================")


if __name__ == '__main__':
    sys.exit(main())
