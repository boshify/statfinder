import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

# Configuration
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
CSE_ID = "YOUR_CSE_ID"

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

def stylish_box(content):
    """Function to return stylish box for Streamlit"""
    return f"""
    <div style="border:1px solid #eee; padding:10px; border-radius:5px; box-shadow:2px 2px 2px #aaa;">
        {content}
    </div>
    """

def get_webpage_content(url):
    """Fetch the webpage content."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        st.warning("Failed to fetch the webpage content.")
        return ""

def extract_content_from_html(html_content):
    """Extract main content from the HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()
    return " ".join(soup.stripped_strings)

def summarize_content_with_gpt4(text_content):
    """Summarize content with GPT-4."""
    response = openai.Completion.create(
        model="gpt-4",
        prompt=f"Provide concise summaries for the main ideas in the following content:\n{text_content}",
        max_tokens=200
    )
    return response.choices[0].text.strip().split("\n")

def search_google_for_statistic(query):
    """Search Google for a statistic related to the query."""
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={CSE_ID}"
    response = requests.get(url).json()
    return response['items'][0]['link'] if 'items' in response else None

def generate_example_usage(statistic, context):
    """Generate example usage for the statistic."""
    response = openai.Completion.create(
        model="gpt-4",
        prompt=f"Given the statistic '{statistic}', provide an example sentence using it in the context of this topic: '{context}'",
        max_tokens=100
    )
    return response.choices[0].text.strip()

def main():
    st.title("StatGrabber 2.0")
    st.write("Enter a URL and discover amazing statistics!")
    url = st.text_input("Enter URL:")

    if st.button("Grab Stats"):
        html_content = get_webpage_content(url)
        text_content = extract_content_from_html(html_content)
        key_points = summarize_content_with_gpt4(text_content)
        
        for key_point in key_points:
            search_query = f"statistics related to {key_point}"
            stat_url = search_google_for_statistic(search_query)
            
            if stat_url:
                stat_text, _ = extract_content_from_html(get_webpage_content(stat_url))
                example_use = generate_example_usage(stat_text, text_content)
                
                content = f"""
                <b>Statistic:</b> {stat_text}<br>
                <b>URL:</b> {stat_url}<br>
                <b>Example Use:</b> {example_use}<br>
                <button onclick="navigator.clipboard.writeText('{stat_text} - Source: {stat_url}')">Copy to clipboard</button>
                """
                st.markdown(stylish_box(content), unsafe_allow_html=True)

if __name__ == '__main__':
    main()
