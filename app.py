import streamlit as st
import openai
from bs4 import BeautifulSoup
import requests

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

def get_webpage_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None

def extract_content_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup(['script', 'style']):
        script.extract()  # Remove script and style tags
    text = soup.get_text()
    # Split the text by lines and remove empty lines
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

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

url = st.text_input("Enter URL:", "Enter a URL for a page or blog post to grab stats for..")

if st.button("Go!"):
    html_content = get_webpage_content(url)
    if html_content:
        text_content = extract_content_from_html(html_content)
        chunks = chunk_text(text_content)
        aggregated_points = []
        chunks = [chunk for chunk in chunks if len(chunk.split()) > 5]
        for text_chunk in chunks:
            response = openai.Completion.create(
            engine="davinci",
            prompt=f"Provide concise one-sentence summaries for the main ideas in the following content:\n{text_chunk}",
            max_tokens=150  # adjust as needed
            )

            key_points = response.choices[0].text.strip().split("\n")
            min_length = 5
            max_length = 150
            key_points = [point for point in key_points if min_length <= len(point.split()) <= max_length]

            aggregated_points.extend(key_points)
        
        # Display the top 10 key points
        for idx, point in enumerate(aggregated_points[:10], 1):
            st.markdown(stylish_box(f"{idx}. {point}"), unsafe_allow_html=True)
    else:
        st.write("Failed to fetch the content.")

# Spacing
for _ in range(3):
    st.write("")

# Footer (About Info)
st.image("https://jonathanboshoff.com/wp-content/uploads/2021/01/Jonathan-Boshoff-2.png", width=50)
st.write("[Made by: Jonathan Boshoff](https://jonathanboshoff.com)")
