import streamlit as st
import openai
from bs4 import BeautifulSoup
import requests
import time
import random

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
url = st.text_input("Enter URL:", "Enter a URL for a page or blog post to grab stats for..")

# List of fun messages for the spinner
fun_messages = [
    "calculating all the pixels...",
    "translating to Martian...",
    "checking for gremlins...",
    "waiting for the stars to align...",
    "flipping bits...",
    "at the speed of light..."
]

def process_url(url):
    with st.spinner(random.choice(fun_messages)):
        html_content = get_webpage_content(url)
        if html_content:
            text_content = extract_content_from_html(html_content)
            chunks = chunk_text(text_content)
            aggregated_points = []
            chunks = [chunk for chunk in chunks if len(chunk.split()) > 5]
            
            # Progress bar demo
            progress = st.progress(0)
            total_chunks = len(chunks)
            for idx, text_chunk in enumerate(chunks, 1):
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
                
                # Update progress bar
                progress.progress(int((idx/total_chunks) * 100))

            # Display the top 10 key points
            for idx, point in enumerate(aggregated_points[:10], 1):
                st.markdown(stylish_box(f"{idx}. {point}"), unsafe_allow_html=True)

        else:
            st.write("Failed to fetch the content.")

if st.button("Go!"):
    process_url(url)

# Footer (About Info)
st.image("https://jonathanboshoff.com/wp-content/uploads/2021/01/Jonathan-Boshoff-2.png", width=50)
st.write("[Made by: Jonathan Boshoff](https://jonathanboshoff.com)")
