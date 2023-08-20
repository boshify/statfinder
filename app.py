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
            margin-bottom: 30px;
        }
        img {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            margin-top: 30px;
        }
        .footer {
            position: absolute;
            bottom: 5%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("StatGrabber")
url = st.text_input("Enter URL:", "Enter a URL for a page or blog post to grab stats for..")

if st.button("Go!"):
    st.write("test is good")

# Footer (About Info)
st.markdown(
    """
    <div class="footer">
        <img src="https://jonathanboshoff.com/wp-content/uploads/2021/01/Jonathan-Boshoff-2.png" alt="Jonathan Boshoff">
        <p>Enter a URL and find statistics you can link to quickly!</p>
        <a href="https://jonathanboshoff.com">Made by: Jonathan Boshoff</a>
    </div>
    """,
    unsafe_allow_html=True,
)
