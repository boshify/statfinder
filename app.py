import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title('H1 and H2 Extractor')

# Input for URL
url = st.text_input('Enter the URL:')

if url:
    try:
        # Fetch the content of the URL
        response = requests.get(url)
        response.raise_for_status()

        # Parse the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract all h1 and h2 tags
        h1_tags = soup.find_all('h1')
        h2_tags = soup.find_all('h2')

        if h1_tags and h2_tags:
            h1_text = h1_tags[0].get_text()

            # Display h2 + h1 formatted list
            for h2 in h2_tags:
                st.write(f'"{h2.get_text()} + {h1_text}"')

        else:
            st.warning('No H1 or H2 tags found on the provided URL.')

    except Exception as e:
        st.error(f"An error occurred: {e}")

