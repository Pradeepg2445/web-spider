# crawler.py

import scrapy
import langid
from scrapy.exceptions import IgnoreRequest
from urllib.parse import urlparse
from helper.baseFunc import console, warning, generate_uuids
from scrapy.crawler import CrawlerProcess
from scrapy.utils.ossignal import install_shutdown_handlers  # Import signal handler installer
from config import fileExtensions
from database import execute_query
from config import DB_GENERAL, DB_INDEXED_KEYWORD, DB_INDEXED_PAGE

class MySpider(scrapy.Spider):
    name = 'myspider'
    collected_urls = set()  # Set to store collected URLs

    def __init__(self, start_url=None, domain_name=None, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        if start_url is not None:
            self.start_urls = [start_url] 
        if domain_name is not None:
            self.domain_name = domain_name


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        try:
            # Check if the page language is English
            page_text = response.text
            if langid.classify(page_text)[0] == 'en':
                # Extract all URLs from the response
                for href in response.css('a::attr(href)').getall():
                    url = response.urljoin(href)
                    if len(url) > 254:
                        warning("THE URL LENGTH IS GREATER THAN 254 CHAR, SO SKIPPING IT")
                        continue

                    if self.is_valid_url(url):
                        if url not in self.collected_urls:
                            print(url)
                            self.collected_urls.add(url)  # Add URL to collected set
                            yield scrapy.Request(url, callback=self.parse)  # Continue crawling recursively
        except (IgnoreRequest, Exception) as e:
            pass  # Ignore exceptions and continue crawling

    def is_valid_url(self, url):
        # Check if the URL is within the allowed domain and is not a file URL
        parsed_url = urlparse(url)
        return parsed_url.netloc == urlparse(self.start_urls[0]).netloc and not self.is_file_url(url)

    def is_file_url(self, url):
        # Check if the URL points to a file
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        return path.endswith(fileExtensions)
        
 
    def closed(self, reason):
        # Initialize an empty set for unique URLs
        unique_urls = set()

        # Group URLs by base URL
        url_dict = {}

        # Group URLs by base URL
        for url in self.collected_urls:
            # Parse the URL to separate the scheme
            parsed_url = urlparse(url)
            scheme = parsed_url.scheme.lower()
            netloc = parsed_url.netloc
            path = parsed_url.path.rstrip('/')

            # Check if it's HTTP or HTTPS
            if scheme in ['https', 'http']:
                base_url = f"{scheme}://{netloc}{path}"
                if base_url not in url_dict:
                    url_dict[base_url] = url

        # Add unique base URLs to the set
        for url in url_dict.values():
            unique_urls.add(url)

        self.insertToTable(unique_urls)






    def insertToTable(self, urls, batch_size=200):
        if not urls:
            return  # Return if the set of URLs is empty
            
        # Convert the set of URLs into a list
        urls_list = list(urls)

        # Determine the number of batches
        num_batches = (len(urls_list) + batch_size - 1) // batch_size

        for i in range(num_batches):
            # Extract URLs for the current batch
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, len(urls_list))
            batch_urls = urls_list[start_idx:end_idx]


            # Generate SQL query for bulk insert with correct number of placeholders
            values = ', '.join([f"('{uuid_}', '{url}')" for uuid_, url in zip(generate_uuids(32), batch_urls)])
            
            query = f"""
                INSERT INTO `{self.domain_name}` (`page_id`, `page_url`)
                VALUES {values}
                ON DUPLICATE KEY UPDATE `page_url` = `page_url`;
            """
                        
            try:
                # Execute the query with the URLs for the current batch
                result = execute_query(query, DB_INDEXED_PAGE, commit=True)
                if result is False:
                    print("Error executing bulk insert.")
            except Exception as e:
                # Handle exceptions, e.g., log the error
                warning(f"Failed to insert URLs into the database: {str(e)}")







def doCrawl(start_url, domain_name):
    try:
        console("CRAWLER IS RUNNING")
        
        process = CrawlerProcess(settings={
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': 100,
        },
        'LOG_LEVEL': 'ERROR'  # Set log level to ERROR to suppress debug information
        })

    # Run the spider with the input URL
        process.crawl(MySpider, start_url=start_url, domain_name=domain_name)
        process.start()
    except (IgnoreRequest, Exception) as e:
        pass  # Ignore exceptions and continue crawling
