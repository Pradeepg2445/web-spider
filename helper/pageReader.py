import requests
from bs4 import BeautifulSoup
import time
from nltk.tokenize import word_tokenize
from spellchecker import SpellChecker
from helper.baseFunc import remove_quotes, extract_top_keywords
import spacy
import nltk



nlp = spacy.load("en_core_web_sm")
nltk.download('punkt')
nltk.download('stopwords')



 
def calculate_spelling_mistake_score(text):
    spell = SpellChecker()
    words = word_tokenize(text.lower())  # Convert text to lowercase here
    misspelled = spell.unknown(words)
    mistake_score = len(misspelled)
    return mistake_score

async def fetch_webpage_keywords(url):
    start_time = time.time()  # Start time for measuring page load time
    
    # Make an HTTP GET request to fetch the webpage content
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title and body text
        title = soup.title.string.strip().lower() if soup.title else ''  # Convert title to lowercase
        body_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        main_content = ' '.join([element.get_text() for tag in body_tags for element in soup.find_all(tag)]) 
       
        main_content = main_content.replace('\n', '') 

        # Remove non-breaking space characters
        main_content = main_content.replace('\u2002', ' ')

        # Perform NLP analysis
        doc = nlp(main_content)

        # Extract meaningful sentences or keywords
        temp = [sent.text for sent in doc.sents if len(sent.text) > 20]  # Example: Consider sentences with more than 20 characters
        body_text = temp[0]
        
        if temp:
            body_text = temp[0]
        else:
            body_text=""
        
        # Calculate spelling mistake score
        spelling_mistake_score = calculate_spelling_mistake_score(body_text)
         
        title_keywords = extract_top_keywords(title, max_keywords=20) 
        if not title_keywords:  # If title keywords are empty
            title_words = title.split() 
            title_keywords = title_words[:20] 
        
        title_key_len = len(title_keywords)
            
        body_keywords = extract_top_keywords(body_text, max_keywords=10)

        title_keywords += extract_top_keywords(body_text, max_keywords=3)
        
        # Count media files
        media_count = len(soup.find_all(['img', 'video', 'audio', 'source', 'track']))
        
        # Calculate page load time
        load_time = time.time() - start_time
        
        # Extract meta keywords and description
        meta_keywords = soup.find('meta', attrs={'name': lambda x: x and x.lower() == 'keywords'})
        meta_description = soup.find('meta', attrs={'name': lambda x: x and x.lower() == 'description'})

        # Combine meta keywords and description into a single array
        meta_content = []
        if meta_keywords:
            meta_content.extend(extract_top_keywords(meta_keywords['content'], max_keywords=5))
        if meta_description:
            meta_content.extend(extract_top_keywords(meta_description['content'], max_keywords=5))

        # Keep only up to 10 unique keywords
        meta_content = list(set(meta_content))

        if meta_content:
            # Select up to two unique keywords from meta_content
            keywords_to_add = meta_content[:2]
            # Add the selected keywords to the title_keywords list
            title_keywords += keywords_to_add

        # Calculate metadata score
        meta_score = len(meta_content)
        
        # Count number of URLs inside the page
        url_count = len(soup.find_all('a'))
        
       # Calculate score based on various factors (e.g., length of title, number of media files, page load time, metadata, URL count)
        title_score = min(title_key_len * 5, 10)  # Max score for title is 10
        body_score = min(len(body_keywords) * 10, 20)   # Max score for body is 20
        media_score = min(media_count * 2, 10)          # Max score for media files is 10
        load_time_score = max(10 - load_time, 0)        # Max score for fast loading time is 10, minimum is 0
        meta_score = min(meta_score, 10)                # Max score for metadata is 10
        url_score = min(url_count / 10, 10)             # Max score for URL count is 10
        spelling_mistake_score = max(10 - spelling_mistake_score, 0)  # Max score for spelling mistakes is 10, minimum is 0

        # Calculate total score
        total_score = title_score + body_score + media_score + load_time_score + meta_score + url_score + spelling_mistake_score

        # Limit total score to 100
        total_score = min(total_score, 100)
         
      
        # Join meaningful sentences into a single string
        meaningful_sentences_string = body_text[:80].strip()
        
        load_time = round(load_time, 4)
        total_score = round(total_score, 4)

        print(meaningful_sentences_string)
        
        return title_keywords, body_keywords, remove_quotes(title), remove_quotes(meaningful_sentences_string), load_time, meta_content, total_score
    else:
        print("Failed to fetch the webpage:", response.status_code)
        return "", "", "", "", "", "", ""
