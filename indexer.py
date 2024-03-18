from config import DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_GENERAL, DB_INDEXED_KEYWORD, DB_INDEXED_PAGE, RUN_INDEXER
import mysql.connector
from helper.pageReader import fetch_webpage_keywords
from helper.baseFunc import arr_to_str, console
import asyncio
import time

# Define database connection details
DB_CONFIG = {
    'host': DB_HOST,
    'port': DB_PORT,
    'user': DB_USERNAME,
    'password': DB_PASSWORD,
}

async def execute_query(query, db_name, commit=False):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute(f"USE {db_name}")
        cursor.execute(query)
        if commit:
            connection.commit()
        if query.strip().lower().startswith('select'):
            result = cursor.fetchall()
            return result
        else:
            return True
    except mysql.connector.Error as e:
        print(f"Error executing query: {e} query:{query}")
        return None
    finally:
        if connection:
            cursor.close()
            connection.close()

async def get_all_table_names():
    try:
        query = "SELECT domain_name FROM domains"
        result = await execute_query(query, DB_GENERAL)
        domain_names = [row[0] for row in result]
        return domain_names
    except Exception as e:
        print(f"Error getting domain names: {e}")
        return []

async def process_domain(domain_name, batch_size=1000):
    try:
        query = f"SELECT page_id, page_url FROM {domain_name} WHERE title IS NULL and isCrawled = '0'"
        offset = 0
        while True:
            batch_query = f"{query} LIMIT {offset}, {batch_size}"
            rows = await execute_query(batch_query, DB_INDEXED_PAGE)
            if not rows:
                break
            tasks = []
            for page_id, page_url in rows:
                tasks.append(update_row_with_json_data(page_id, page_url, domain_name))
            await asyncio.gather(*tasks)
            offset += batch_size
    except Exception as e:
        print(f"Error processing domain '{domain_name}': {e}")


async def ensure_words_table_exists(table_suffix, db_name):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Select the appropriate database
        cursor.execute(f"USE {db_name}")

        table_name = f"words_{table_suffix}"
        create_table_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` (keyword VARCHAR(64) NOT NULL, table_name VARCHAR(64) NOT NULL, page_id VARCHAR(64) NOT NULL, create_time TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP)"

        cursor.execute(create_table_query)
        connection.commit()
    except mysql.connector.Error as e:
        print(f"Error creating table: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

async def update_row_with_json_data(page_id, page_url, domain_name):
    try:
        update_query = f"UPDATE {domain_name} SET isCrawled='1' WHERE page_id='{page_id}'"
        await execute_query(update_query, DB_INDEXED_PAGE, True)
        
        result = await fetch_webpage_keywords(page_url)

        if result is None or len(result) != 7:
            print(f"Skipping update for page_id '{page_id}' due to invalid data.")
            return

        title_keywords, body_keywords, title, meaningful_sentences_string, load_time, meta_content, total_score = result

        title_str = arr_to_str(title_keywords)
        meta_str = arr_to_str(meta_content)
        body_str = arr_to_str(body_keywords)

        update_query = f"UPDATE {domain_name} SET title_string='{title}', body_string='{meaningful_sentences_string}', title='{title_str}', meta='{meta_str}', body='{body_str}', load_time='{load_time}', score='{total_score}' WHERE page_id='{page_id}'"
        await execute_query(update_query, DB_INDEXED_PAGE, True)

        for keyword in title_keywords:
            table_suffix = keyword.lower() if len(keyword) == 1 and (keyword.isalpha() or keyword.isdigit()) else keyword.lower()[:2]
            await ensure_words_table_exists(table_suffix, DB_INDEXED_KEYWORD)  # Ensure the table exists
            table_name = f"words_{table_suffix}"
            insert_query = f"INSERT INTO `{table_name}` (keyword, table_name, page_id) VALUES ('{keyword}', '{domain_name}', '{page_id}')"
            await execute_query(insert_query, DB_INDEXED_KEYWORD, True)
    except Exception as e:
        print(f"Error updating row with page_id '{page_id}': {e}")


async def doIndex():
    if not RUN_INDEXER:
        return
    try:
        console("CORN RUNNING")
        domain_names = await get_all_table_names()
        await asyncio.gather(*[process_domain(domain_name, 100) for domain_name in domain_names])
    except Exception as e:
        print(f"Error updating domains with JSON data: {e}")

# Example usage
asyncio.run(doIndex())
