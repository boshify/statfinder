import requests
from bs4 import BeautifulSoup
import re

def get_content_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = soup.find_all('p')
    content = [p.get_text() for p in paragraphs if p.get_text()]
    return content

def is_statistic(text):
    if re.search(r'\d', text):
        return True
    return False

def format_output(data_list, main_url):
    output = "**StatGrabber**\n"
    output += "Enter a URL and find statistics you can link to quickly!\n\n"
    output += f"Enter URL:\n[{main_url}]({main_url})\n\n"
    
    for idx, (text, url) in enumerate(data_list, 1):
        if is_statistic(text):
            output += f"{idx}.\n"
            output += f"#### Statistic:\n"
            output += f"{text}\n\n"
            output += f"#### Example:\n"
            output += f"In a recent discussion on cryptocurrencies, I mentioned that '{text}'.\n\n"
            output += f"#### URL:\n"
            output += f"[{url}]({url})\n\n"
    
    return output

# Use the provided URL
url = "https://cointelegraph.com/news/mineflation-cost-to-mine-one-bitcoin-in-the-us-rises-from-5k-to-17k-in-2023"
content = get_content_from_url(url)

# Assuming URLs are extracted from the same page, using a placeholder list of URLs for this example
urls = [url for _ in content]

# Pair each content piece with its URL
extracted_data = list(zip(content, urls))

print(format_output(extracted_data, url))
