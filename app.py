import streamlit as st
import requests
import openai
import re

# Assuming you have set up the API keys and CSE_ID as before
API_KEY = st.secrets["secrets"]["GOOGLE_API_KEY"]
CSE_ID = st.secrets["secrets"]["CSE_ID"]
OPENAI_API_KEY = st.secrets["secrets"]["OPENAI_API_KEY"]


def extract_key_points_from_text(text):
    response = openai.Completion.create(
      engine="davinci",
      prompt=f"Summarize the following content into 10 key points:\n\n{text}",
      max_tokens=200
    )
    return response.choices[0].text.strip().split('\n')

def fetch_stat_from_google(query):
    GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': f"statistics about {query}",
        'key': API_KEY,
        'cx': CSE_ID,
    }
    response = requests.get(GOOGLE_CSE_URL, params=params)
    data = response.json()
    results = []
    if data.get("items"):
        for item in data["items"]:
            if any(char.isdigit() for char in item["snippet"]):
                results.append({
                    "stat": item["snippet"],
                    "link": item["link"]
                })
    return results

def get_trust_score_with_gpt(stat):
    try:
        response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Score this information from 1-10 on a scale of believability. 10 being highly believable and 1 being hardest to believe:\n\n{stat}"}
            ]
        )
        score = re.search(r'\d+', response.choices[0].message['content'].strip())
        if score:
            return int(score.group())
        else:
            return 5
    except Exception as e:
        st.error(f"Error in get_trust_score_with_gpt: {e}")
        return 5

# Streamlit UI
url = st.text_input("Insert the URL you want to enhance with statistics:")

if url:
    response = requests.get(url)
    key_points = extract_key_points_from_text(response.text)
    
    summarized_text = "\n".join(key_points)
    st.write("Summarized Text:")
    st.write(summarized_text)
    
    for point in key_points:
        stats = fetch_stat_from_google(point)
        for stat in stats:
            trust_score = get_trust_score_with_gpt(stat["stat"])
            st.write(f"Statistic: {stat['stat']}")
            st.write(f"Statistic URL: {stat['link']}")
            st.write(f"Trust Score: {trust_score}/10")
            st.write(f"Example Use: `{point}`")
