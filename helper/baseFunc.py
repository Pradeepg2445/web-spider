from config import console_colors
from urllib.parse import urlparse
import re
import uuid
from nltk.corpus import stopwords
import nltk


def generate_uuids(num_uuids=32):
    uuids = []
    for _ in range(num_uuids):
        uuids.append(str(uuid.uuid4()))
    return uuids

def console(message, color='blue'):
    color_code = console_colors.get(color.lower(), console_colors['default'])
    print(color_code + "********************** " + message + " **********************" + console_colors['default'])


def warning(message, color='red'):
    console(message, color)


def extract_name_from_url(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc:
        netloc = parsed_url.netloc
        # Remove special characters using regular expression
        netloc = re.sub(r'[^a-zA-Z0-9]', '_', netloc)
        # Convert to lowercase
        netloc = netloc.lower()
        return netloc
    else:
        return None


def filter_urls(urls): # REMOVING THE DUPLICATE URL BY USING # URL
    base_urls = set()
    for url in urls:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        base_urls.add(base_url)
    return list(base_urls)

def arr_to_str(arr):
    if not arr:
        return ""
    else:
        return ', '.join(str(x) for x in arr)
    
    
def remove_quotes(string):
    return string.replace("'", "").replace('"', '').replace('`', '')


def extract_top_keywords(text, max_keywords):
    if text is None or text.strip() == '':
        return []

    # Tokenize the text
    words = nltk.word_tokenize(text)

    # Filter out stopwords and unwanted characters
    stop_words = set(stopwords.words('english'))
    unwanted_characters = ["'", '"', '`']
    words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words 
             and all(char not in word for char in unwanted_characters)]

    # Calculate word frequencies
    word_freq = nltk.FreqDist(words)

    # Get the top keywords
    top_keywords = list(word_freq.keys())[:max_keywords]

    # Convert keywords to lowercase
    top_keywords_lower = [keyword.lower() for keyword in top_keywords]

    return top_keywords_lower

