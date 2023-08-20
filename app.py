import streamlit as st
from bs4 import BeautifulSoup
import requests
import re

# Function to extract statistics from a URL
def extract_stats_from_url(url):
    try:
        # Get the content of the webpage
        content = requests.get(url).content
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove unwanted script and style tags
        for script in soup(['script', 'style']):
            script.extract()
        
        # Extract statistics using a regex pattern
        # This pattern captures numbers, including those formatted with commas or decimals
        pattern = re.compile(r'(?<!\d)[+-]?[0-9]{1,3}(?:,?[0-9]{3})*(?:\.\d+)?(?!\d)')
        
        # Create a list of potential sentences that contain statistics
        text = soup.get_text()
        sentences = text.split('.')
        stat_sentences = [sentence for sentence in sentences if pattern.search(sentence)]
        
        return stat_sentences
    except Exception as e:
        st.write(f"An error occurred: {e}")
        return []

# Streamlit app
def app():
    st.title("StatFinder")
    st.write("Enter a URL and find statistics you can link to quickly!")

    # Text input for the URL
    url = st.text_input("Enter URL:")

    if url:
        # Call function to extract statistics
        stats = extract_stats_from_url(url)

        # Remove duplicate stats
        unique_stats = list(set(stats))

        if not unique_stats:
            st.write("No statistics found in the provided URL.")
            return

        # Display each statistic
        for statistic in unique_stats:
            with st.beta_container():
                # Using markdown to make content bold
                st.markdown(f"**Statistic:** {statistic.strip()}")
                st.markdown(f"**Link:** [Source]({url})")
                st.markdown(f"**Example Use:** 'According to a recent report, \"{statistic.strip()}\" ([source]({url}))'")

# Run the Streamlit app
if __name__ == "__main__":
    app()
