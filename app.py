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
        #infoBox {
            border: 1px solid white;  # Adjusting to match the theme
            padding: 10px;
            margin-top: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("StatGrabber")
st.write("Enter a URL and find statistics you can link to quickly!")

url = st.text_input("Enter URL:", "Enter a URL for a page or blog post to grab stats for..")

if st.button("Go!"):
    # Placeholder for your URL processing logic, or OpenAI API calls
    st.write("Processing the URL...")

# Adding the information box
st.markdown(
    """
    <div id="infoBox">
      <h2>About the OpenAI API</h2>
      To use a GPT model via the OpenAI API, you’ll send a request containing the inputs and your API key, 
      and receive a response containing the model’s output...
      <!-- add all the relevant information provided previously here -->
    </div>
    """,
    unsafe_allow_html=True,
)

# Spacing
for _ in range(3):
    st.write("")

# Footer (About Info)
st.image("https://jonathanboshoff.com/wp-content/uploads/2021/01/Jonathan-Boshoff-2.png", width=50)
st.write("[Made by: Jonathan Boshoff](https://jonathanboshoff.com)")
