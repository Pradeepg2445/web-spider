
from crawler import doCrawl
from helper.baseFunc import console, warning , extract_name_from_url
from database import execute_query
from config import DB_GENERAL, DB_INDEXED_KEYWORD, DB_INDEXED_PAGE
 
 
def async_task(payload=None):
    try:
        url = payload.get("siteUrl") 
        
        if url is not None: 
            domain_name = extract_name_from_url(url)
           
            result = execute_query(f"""
                                   INSERT IGNORE INTO domains (url, domain_name, user_id) 
                                    VALUES( '{url}', '{domain_name}', '{payload.get("user_id")}'  )
                                   """, DB_GENERAL, True)
            
            result = execute_query(f"""
        CREATE TABLE IF NOT EXISTS `{domain_name}` (
            `page_id` CHAR(36) PRIMARY KEY,
            `page_url` VARCHAR(255) NOT NULL,
            `title` TEXT,
            `meta` TEXT,
            `body` TEXT,
            `load_time` VARCHAR(10) DEFAULT NULL,
            `score` VARCHAR(10) DEFAULT NULL,
            `title_string` TEXT,
            `body_string` TEXT,
            `isCrawled`  VARCHAR(1) DEFAULT 0,
            `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """, DB_INDEXED_PAGE, True)


            doCrawl(url, domain_name)
        else:
             warning("URL NOT FOUND FOR CRAWLING")

        console("Async task completed")
    except Exception as e:
        print("Async task encountered an error:", e)
