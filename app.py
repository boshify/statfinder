import streamlit as st
import openai
from bs4 import BeautifulSoup
import requests
import re

# Load secrets
secrets = st.secrets["secrets"]
GOOGLE_API_KEY = secrets["GOOGLE_API_KEY"]
CSE_ID = secrets["CSE_ID"]
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

def chunk_text(text, max_length=1500):
    sentences = text.split('.')
    chunks = []
    chunk = ""
    for sentence in sentences:
        if len(chunk) + len(sentence) < max_length:
            chunk += sentence + "."
        else:
            chunks.append(chunk)
            chunk = sentence + "."
    if chunk:
        chunks.append(chunk)
    return chunks

def stylish_box(content):
    box_style = """
    <div style="
        border: 2px solid #f1f1f1;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0px;
        box-shadow: 2px 2px 12px #aaa;">
        {content}
    </div>
    """
    return box_style.format(content=content)

st.title("StatGrabber")
st.write("Enter a URL and find statistics you can link to quickly!")
url = st.text_input("Enter URL:")

def get_webpage_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        return response.text if response.status_code == 200 else None
    except:
        return None

def extract_content_from_html(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    for script in soup(["script", "style"]):
        script.extract()
    return " ".join(soup.stripped_strings)

def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={CSE_ID}"
    response = requests.get(url).json()
    if 'items' in response:
        for item in response['items']:
            link = item.get('link')
            if link:
                return link
    return None

def extract_statistic_from_url(stat_url):
    page_content = get_webpage_content(stat_url)
    if not page_content:
        return None, stat_url
    page_text = extract_content_from_html(page_content)
    
    # For now, just return the first 300 characters. This can be improved further.
    return page_text[:300], stat_url

def process_url(main_url):
    html_content = get_webpage_content(main_url)
    if html_content:
        text_content = extract_content_from_html(html_content)
        chunks = chunk_text(text_content)
        aggregated_points = []
        
        for text_chunk in chunks:
            response = openai.Completion.create(
                engine="davinci",
                prompt=f"Provide concise summaries for the main ideas in the following content:\n{text_chunk}",
                max_tokens=150
            )
            key_points = response.choices[0].text.strip().split("\n")
            aggregated_points.extend(key_points)
            
        for idx, point in enumerate(aggregated_points[:10], 1):
            search_query = f"statistics related to {point}"
            stat_url = search_google(search_query)
            
            if stat_url:
                statistic, _ = extract_statistic_from_url(stat_url)
            else:
                statistic = None

            if statistic:
                content = f"<h3>{idx}. {point}</h3><br>Statistic: {statistic}<br>Example: In a recent discussion on cryptocurrencies, I mentioned that '{statistic}'.<br><br>URL: {stat_url}"
            else:
                content = f"<h3>{idx}. {point}</h3><br>No relevant statistic found."
            st.markdown(stylish_box(content), unsafe_allow_html=True)
    else:
        st.error("Unable to fetch the content from the provided URL. Please check if the URL is correct and try again.")

if url:
    process_url(url)

st.sidebar.header("About")
st.sidebar.write("StatGrabber is an AI-powered tool to help you quickly find and cite statistics related to your article or content.")
st.sidebar.write("This tool uses GPT-3.5-turbo and other AI models to analyze the content and fetch relevant statistics.")
