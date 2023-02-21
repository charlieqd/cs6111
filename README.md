1. Chenhao Liu, cl4298
   Hanzhe Zhang, hz2742
2. List of files: query.py, stop_words.txt, transcript.txt, README
3. How to run the program:
Install google-api-client package, sudo pip3 install --upgrade google-api-python-client
Install sklearn: pip3 install --upgrade setuptools wheel pip
		 pip3 install scikit-learn
Run: python3 query.py <google api key> <google engine id> <precision> <query>
example: python3 query.py AIzaSyCMb6xd4NnbwRHgXUPVA5dTfFxaAN3CuLE a95a1235f40abcb47 0.9 "brin"
4. Internal design of the project:
a.main(query): Entry point. It takes user's input(Search API key, engine ID, precision and query keyword) and builds the google search engine service, which takes the input query and return top 10 results of filetype html. Then it asks for user's feedback to determine which document is relevant. If the precision meets the required precision or there is no document returned, it will stop searching. Otherwise it will call function augment to add new words into the query. The new query will be used to search again until it meets the requirement or no result returned.

b. augment: It is used to pick up two new words and generate a new query(including ordering) using Rocchio's Algorithm.

c. read_words: It reads stop_words.txt, which is used in the CountVectorizer

d. log_transcript: prints the text to user and also write the transcript into the file, transcript.txt
 
5. Description of query-modification method: For the returned documents, users split them into two categories, relevant and irrelevant documents. It uses CountVectorizer to count word frequency for each category. We defined beta as 0.85 and gamma as 0.15 to use Rocchio's Algorithm to pick up two new words. For each word, it has an initial value as 0. Then if the final value of the word will be beta*frequency_in_relevant_doc/total_num_words_in_relevant_doc - gamma*frequency_in_irrelevant_doc/total_num_words_in_irrelevant_doc. Then we skipped the words which are already inside the query and pick up two new words with highest value in the order appended after the original query.

6. Google Custom Search Engine JSON API Key: AIzaSyCMb6xd4NnbwRHgXUPVA5dTfFxaAN3CuLE
   Engine ID:  a95a1235f40abcb47