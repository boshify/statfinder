import streamlit as st
import requests
import json
import openai

# Set Streamlit page configuration
st.set_page_config(
    page_title="URL Statistics Finder",
    page_icon="🔍",
    layout="wide",
)

# Fetch secrets
API_KEY = st.secrets["GOOGLE_API_KEY"]
CSE_ID = st.secrets["CSE_ID"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

def fetch_stats_from_google(query):
    stats = []
    try:
        GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': query,
            'key': API_KEY,
            'cx': CSE_ID,
        }
        response = requests.get(GOOGLE_CSE_URL, params=params)
        data = response.json()
        
        for item in data.get("items", []):
            title = item["title"]
            link = item["link"]
            stats.append({"stat": title, "link": link})
    except Exception as e:
        stats.append({"stat": f"Error: {str(e)}", "link": "#"})
    return stats

def get_insight_from_openai(link):
    try:
        response = openai.Completion.create(
          engine="davinci",
          prompt=f"Summarize the main topic or content of this link: {link}",
          max_tokens=150,
          n=1,
          stop=None,
          temperature=0.7
        )
        insight = response.choices[0].text.strip()
        # Ensure the insight is not too short
        if len(insight.split()) < 5:
            return "Insight not available."
        return insight
    except:
        return "Unable to fetch insight."

# Streamlit layout and components
c30, c31 = st.columns([10.5, 1])

with c30:
    st.title("URL Statistics Finder")

with st.expander("ℹ - About the App"):
    st.write(
        """
- This application aims to find relevant statistics about the topic of a given URL.
- To do so, simply enter the URL you're interested in.
- The app will provide you with a list of relevant statistics, links, and insights.
	    """
    )

st.markdown("----")

c1, c2 = st.columns([1.5, 4])

with c1:
    url = st.text_input('Insert the URL you want to search for statistics:')
    
    if url:
        stats = fetch_stats_from_google(url)

        with c2:
            for s in stats:
                if "Error" in s['stat']:
                    st.error(s['stat'])  # Display the error message
                else:
                    insight = get_insight_from_openai(s['link'])
                    truncated_link = (s['link'][:50] + '...') if len(s['link']) > 50 else s['link']
                    st.markdown(f"**Stat:** {s['stat']}")
                    st.markdown(f"**Link:** [{truncated_link}]({s['link']})")
                    st.markdown(f"**Insight:** {insight}")
                    st.markdown(f"**Example Usage:** {s['stat']} [source]({s['link']})")
                    st.markdown("---")

st.markdown("----")
