import streamlit as st
import openai

# Load secrets
secrets = st.secrets["secrets"]
GOOGLE_API_KEY = secrets["GOOGLE_API_KEY"]
CSE_ID = secrets["CSE_ID"]
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

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
        }
        img {
            width: 300px;
            border-radius: 50%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.image("https://jonathanboshoff.com/wp-content/uploads/2021/01/Jonathan-Boshoff-2.png", caption="")
st.title("StatGrabber")
st.write("Enter a URL and find statistics you can link to quickly!")
st.write("[Made by: Jonathan Boshoff](https://jonathanboshoff.com)")

url = st.text_input("Enter URL:", "Enter a URL for a page or blog post to grab stats for..")

if st.button("Go!"):
    st.write("test is good")

