import streamlit as st
import openai
from bs4 import BeautifulSoup
import requests
import time
import random
import re
import lxml

# Load secrets
secrets = st.secrets["secrets"]
GOOGLE_API_KEY = secrets["GOOGLE_API_KEY"]
CSE_ID = secrets["CSE_ID"]
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Added and refined patterns to target data, findings, proofs, and studies.
STATISTIC_PATTERNS = [
    r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?%?)',  # General numbers and percentages
    r'(\d+\s*in\s*\d+)',  # Ratios like 1 in 5
    r'(study|research|survey|data|finding)s?\s*(shows?|found|reveals?|suggests?|indicates?)',  # Indicating a study or finding
    r'(one|two|three|four|five|six|seven|eight|nine|ten)\s*out of (ten|a hundred)',  # Written ratios
    r'(evidence|proof|result)s?\s*(shows?|suggests?|indicates?)'  # Indicating evidence or proof
]

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

# Styling
st.markdown(
    """
    <style>
        .reportview-container {
            background: black;
            color: white;
        }
        h1 {
            font-size: 50px;
            margin-bottom: 30px;
        }
        img {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            margin-top: 30px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("StatGrabber")
st.write("Enter a URL and find statistics you can link to quickly!")
url = st.text_input("Enter URL:")

fun_messages = [
    "Calculating all the pixels...",
    "Finding the best statistics...",
    "Analyzing the content...",
    "Thinking really hard...",
    "Grabbing some coffee...",
    "Doing some cool AI stuff..."
]

def get_webpage_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        return response.text if response.status_code == 200 else None
    except:
        return None

def is_html(content):
    return content is not None and any(tag in content.lower() for tag in ['<html', '<body', '<head', '<script', '<div', '<span', '<a'])

def extract_content_from_html(html_content):
    if not is_html(html_content):
        return ""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
    except Exception:
        soup = BeautifulSoup(html_content, 'lxml')

    for script in soup(["script", "style"]):
        script.extract()
    return " ".join(soup.stripped_strings)

def show_loading_message(duration=6):
    start_time = time.time()
    while time.time() - start_time < duration:
        st.text(random.choice(fun_messages))
        time.sleep(2)

def is_valid_content(sentence):
    return len(sentence.split()) >= 5 and all(symbol not in sentence for symbol in ['{', '}', '%', '='])

def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={CSE_ID}"
    response = requests.get(url).json()
    return response['items'][0]['link']

def score_statistic(statistic, keywords):
    score = 0
    for keyword in keywords:
        score += statistic.lower().count(keyword.lower())
    return score

def extract_statistic_from_url(url, keywords):
    page_content = get_webpage_content(url)
    if not page_content:
        return None, url
    page_text = extract_content_from_html(page_content)
    
    potential_statistics = []

    for pattern in STATISTIC_PATTERNS:
        matches = re.finditer(pattern, page_text)
        for match in matches:
            start_idx = match.start()
            end_idx = match.end()

            # Extract sentences containing the matched pattern for context.
            start_sentence_idx = page_text.rfind('.', 0, start_idx) + 1  # start of the sentence
            end_sentence_idx = page_text.find('.', end_idx)  # end of the sentence
            surrounding_text = page_text[start_sentence_idx:end_sentence_idx + 1].strip()

            # Ensure the extracted text is a complete sentence.
            if surrounding_text and surrounding_text[-1] == '.' and is_valid_content(surrounding_text):
                potential_statistics.append((surrounding_text.strip(), score_statistic(surrounding_text, keywords)))

    # Sorting the potential statistics by their scores
    potential_statistics.sort(key=lambda x: -x[1])
    
    if potential_statistics:
        return potential_statistics[0][0], url
    return None, url


def process_url(url):
    show_loading_message()
    html_content = get_webpage_content(url)
    if html_content:
        text_content = extract_content_from_html(html_content)
        chunks = [chunk for chunk in chunk_text(text_content) if is_valid_content(chunk)]
        
        progress = st.progress(0)
        total_chunks = len(chunks)
        aggregated_points = []
        
        for idx, text_chunk in enumerate(chunks):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": f"Provide concise summaries for the main ideas in the following content:\n{text_chunk}"}
                ]
            )
            key_points = response.choices[0]["message"]["content"].strip().split("\n")
            key_points = [point for point in key_points if 5 <= len(point.split()) <= 150]
            aggregated_points.extend(key_points)
            progress.progress(int((idx/total_chunks) * 100))
        
        for idx, point in enumerate(aggregated_points[:10], 1):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": f"Provide a concise summary for the following statement:\n{point}"}
                ]
            )
            summarized_point = response.choices[0]["message"]["content"].strip()
            summarized_point = point if not is_valid_content(summarized_point) else summarized_point

            time.sleep(1.5)
            search_query = f"statistics 2023 {summarized_point}"
            statistic, stat_url = extract_statistic_from_url(search_google(search_query))
            
            if statistic:
                content = f"{idx}. {summarized_point}<br><br>Statistic: {statistic}<br>URL: {stat_url}<br><button onclick=\"navigator.clipboard.writeText('{statistic} - Source: {stat_url}')\">Copy to Clipboard</button>"
                st.markdown(stylish_box(content), unsafe_allow_html=True)
    else:
        st.error("Error fetching the webpage content. Please ensure the URL is correct and try again.")

if url:
    process_url(url)
