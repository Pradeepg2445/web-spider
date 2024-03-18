from database import execute_query_async
from config import DB_GENERAL, DB_INDEXED_KEYWORD
import string
import asyncio

async def database_setup():
    letters = string.ascii_lowercase
    digits = string.digits

    # Generate queries for single-letter combinations
    letter_queries = [f"CREATE TABLE IF NOT EXISTS `words_{letter}` (`keyword` varchar(64) NOT NULL, `table_name` varchar(64) NOT NULL, `page_id` varchar(64) NOT NULL, `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP);" for letter in letters]

    # Generate queries for single-digit numbers
    digit_queries = [f"CREATE TABLE IF NOT EXISTS `words_{digit}` (`keyword` varchar(64) NOT NULL, `table_name` varchar(64) NOT NULL, `page_id` varchar(64) NOT NULL, `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP);" for digit in digits]

    # Generate queries for two-letter combinations (aa to zz)
    two_letter_queries = [f"CREATE TABLE IF NOT EXISTS `words_{combination}` (`keyword` varchar(64) NOT NULL, `table_name` varchar(64) NOT NULL, `page_id` varchar(64) NOT NULL, `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP);" for combination in [f'{c1}{c2}' for c1 in letters for c2 in letters]]

    # Generate queries for two-digit numbers
    two_digit_queries = [f"CREATE TABLE IF NOT EXISTS `words_{str(i).zfill(2)}` (`keyword` varchar(64) NOT NULL, `table_name` varchar(64) NOT NULL, `page_id` varchar(64) NOT NULL, `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP);" for i in range(100)]

    # Generate queries for number-letter combinations like "1a", "1b", "1c", ...
    number_letter_queries = [f"CREATE TABLE IF NOT EXISTS `words_{str(num)}{letter}` (`keyword` varchar(64) NOT NULL, `table_name` varchar(64) NOT NULL, `page_id` varchar(64) NOT NULL, `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP);" for num in range(10) for letter in letters]

    # Generate queries for letter-number combinations like "a1", "b1", "c1", ...
    letter_number_queries = [f"CREATE TABLE IF NOT EXISTS `words_{letter}{str(num)}` (`keyword` varchar(64) NOT NULL, `table_name` varchar(64) NOT NULL, `page_id` varchar(64) NOT NULL, `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP);" for letter in letters for num in range(10)]


    # Combine all queries
    all_queries = letter_queries + digit_queries + two_letter_queries + two_digit_queries + number_letter_queries + letter_number_queries

    # Define the general query to create the general table
    general_query = """
         CREATE TABLE IF NOT EXISTS  `domains` (
            `domain_name` varchar(128) NOT NULL UNIQUE,
            `url` varchar(255) NOT NULL UNIQUE,
            `is_crawled` int DEFAULT 0,
            `is_indexed` int DEFAULT 0,
            `user_id` varchar(128) DEFAULT NULL,
            `is_deleted` int DEFAULT 0,
            `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (`domain_name`)
            );
        """
    
    # Execute all queries
    await execute_query_async(general_query, DB_GENERAL)
    # await asyncio.gather(*(execute_query_async(query, DB_INDEXED_KEYWORD) for query in all_queries))

    return "Database Created!"

# Example usage:
# asyncio.run(database_setup())
