import streamlit as st
from bs4 import BeautifulSoup
import requests
import re

# Regex pattern to identify sentences with potential statistics
STATISTIC_PATTERN = r'([^.]*?(?:\d{1,3}(?:,\d{3})*(?:\.\d+)?%|(?:1 in \d+)|(?:1 of \d+)|(?:\$\d{1,3}(?:,\d{3})*(?:\.\d+)?)[^.]*\.)'

def stylish_box(statistic, url):
    box_content = f"""
    <strong>Statistic:</strong> {statistic}<br>
    <strong>URL:</strong> <a href="{url}" target="_blank">{url}</a><br>
    <strong>Example:</strong> In a recent discussion, I mentioned that '{statistic}'.
    """
    box_style = f"""
    <div style="
        border: 2px solid #f1f1f1;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0px;
        box-shadow: 2px 2px 12px #aaa;">
        {box_content}
    </div>
    """
    return box_style

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

def extract_statistics(text_content, url):
    matches = re.findall(STATISTIC_PATTERN, text_content)
    return [stylish_box(statistic, url) for statistic in matches[:10]]

def process_url(url):
    html_content = get_webpage_content(url)
    if html_content:
        text_content = extract_content_from_html(html_content)
        statistics_boxes = extract_statistics(text_content, url)
        
        for box in statistics_boxes:
            st.markdown(box, unsafe_allow_html=True)
    else:
        st.error("Unable to fetch the content from the provided URL. Please check if the URL is correct and try again.")

st.title("StatGrabber")
st.write("Enter a URL and find statistics you can link to quickly!")
url = st.text_input("Enter URL:")

if url:
    process_url(url)

st.sidebar.header("About")
st.sidebar.write("StatGrabber is a tool to help you quickly find and cite statistics related to your article or content.")
