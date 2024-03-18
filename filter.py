from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
import string
import time
from helper.baseFunc import  extract_top_keywords
from config import DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_GENERAL, DB_INDEXED_KEYWORD, DB_INDEXED_PAGE, RUN_INDEXER
from database import execute_query

# def calculate_similarity(text1, objects):
#     similarities = []
    
#     # Initialize the vectorizer
#     vectorizer = TfidfVectorizer()

#     # Fit and transform the vectorizer with single array
#     tfidf_matrix1 = vectorizer.fit_transform([text1])

#     for obj in objects:
#         # Concatenate relevant fields
#         text2 = obj.get('title_string', '') + ' ' + \
#                 obj.get('body', '') + ' ' + \
#                 obj.get('meta', '') + ' ' + \
#                 obj.get('page_url', '')  # Add a space here
        
#         # Transform the text using the pre-fitted vectorizer
#         tfidf_matrix2 = vectorizer.transform([text2])
        
#         # Calculate cosine similarity
#         similarity = cosine_similarity(tfidf_matrix1, tfidf_matrix2)[0][0]

#         # If similarity is 0, skip appending to the list
#         if similarity == 0:
#             continue

#         similarities.append((obj, similarity))

#     # Sort similarities based on similarity value in descending order
#     similarities.sort(key=lambda x: x[1], reverse=True)
    
#     # Return only the top 10 similarities
#     return similarities[:10]

def calculate_similarity(text1, objects):
    similarities = []
    processed_urls = set()  # Set to store processed page_url values
    
    # Initialize the vectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform the vectorizer with single array
    tfidf_matrix1 = vectorizer.fit_transform([text1])

    for obj in objects:
        # Extract the page_url from the object
        page_url = obj.get('page_url', '')

        # Skip processing if page_url is already processed
        if page_url in processed_urls:
            continue
        
        # Concatenate relevant fields
        text2 = obj.get('title_string', '') + ' ' + \
                obj.get('body', '') + ' ' + \
                obj.get('meta', '') + ' ' + \
                page_url  # Add a space here
        
        # Transform the text using the pre-fitted vectorizer
        tfidf_matrix2 = vectorizer.transform([text2])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix1, tfidf_matrix2)[0][0]

        # If similarity is 0, skip appending to the list
        if similarity == 0:
            continue

        # Add the page_url to the set of processed URLs
        processed_urls.add(page_url)

        # Append object with similarity and total_score to the list
        similarities.append((obj, similarity, obj.get('total_score', 0)))

    # Sort similarities based on similarity value in descending order
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Return only the top 10 similarities
    top_10 = similarities[:10]

    # Sort the top 10 from 4rd to 10th based on total_score
    top_10[2:] = sorted(top_10[3:], key=lambda x: x[2], reverse=True)
    
    return top_10


def getResults(UserQuery):
    queryArray = extract_top_keywords(UserQuery, 15)
    if not queryArray:
        temp = UserQuery.split() 
        queryArray = temp[:20]

    results = []

    for word in queryArray:
        table_name = ""
        if len(word) == 1:
            table_name = f"words_{word}"
        elif len(word) >= 2:
            table_name = f"words_{word[:2]}"
        
        table_name=table_name.lower()

        if table_exists(table_name, DB_INDEXED_KEYWORD):
            query = f"SELECT table_name, page_id FROM {table_name} WHERE keyword = '{word}'"
            table_results = execute_query(query, DB_INDEXED_KEYWORD)

           
            temp_1=convert_to_dict_list(table_results)
            table_results_2 =  select_pages(temp_1)

            results.extend(table_results_2)
 
    return calculate_similarity(UserQuery, results)

def convert_to_dict_list(data):
    if not data:
        return []
    
    result = {}
    for item in data:
        table_name = item[0]
        page_id = item[1]
        if table_name in result:
            result[table_name].append(page_id)
        else:
            result[table_name] = [page_id]
    
    dict_list = [{'table_name': table_name, 'page_id': page_ids} for table_name, page_ids in result.items()]
    return dict_list



def select_pages(temp_1):
    results_list = []
    for entry in temp_1:
        table_name = entry['table_name']
        page_ids = entry['page_id']
        
        if table_exists(table_name, DB_INDEXED_PAGE):
            page_id_str = ', '.join([f"'{s}'" for s in page_ids])
            # Open the table and select pages where they are found
            query = f"SELECT page_id, page_url, title, meta, body, load_time, score, title_string, body_string, isCrawled FROM {table_name} WHERE page_id IN ({page_id_str})"

            # Execute the query with page_ids as parameters
            result = execute_query(query, DB_INDEXED_PAGE)

            # Check if there are any rows in the result
            if result:
                # Convert each row tuple to a dictionary with column names as keys
                for row in result:
                    row_dict = dict(zip(('page_id', 'page_url', 'title', 'meta', 'body', 'load_time', 'score', 'title_string', 'body_string', 'isCrawled'), row))
                    results_list.append(row_dict)
            else:
                print(f"No results returned from table {table_name}.")
        else:
            print(f"Table {table_name} not found.")

    return results_list




def table_exists(table_name, db_name):
    # Use the database connection to execute a query to check if the table exists
    query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{db_name}' AND table_name = '{table_name}'"
    result = execute_query(query, db_name)
    return result[0][0] > 0