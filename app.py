# Import necessary libraries
from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
import time
import streamlit.components.v1 as components

# Load environment variables
load_dotenv()

# Configure Google API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize GenerativeModel
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Function to get Gemini response with a typewriter effect
def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    prompt_response = []
    for chunk in response:
        st.write(chunk.text, type="default")   
        prompt_response.append(chunk.text)
    return prompt_response    

# Set page configuration
st.set_page_config(page_title="Water Bot Demo", page_icon=":droplet:")

# Define header and title
st.title("Water Bot Chat Interface")
st.markdown("---")

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
     

# User input and submit button
input_text = st.text_input("Input: ", key="input")
submit = st.button("Ask the question", key="submit_button")

# Process user input and get response

if submit and input_text:
    st.subheader(f'You: {input_text}')
    response = get_gemini_response(input_text)
    for t in response:
        st.session_state['chat_history'].append(t)

    response_history = ''
    for chunk in response:
        response_history += chunk 

# Use st.markdown to add custom CSS for sidebar width
st.markdown(
    """
    <style>
    .css-1l02zno {
        width: 350px !important; /* Adjust the width as needed */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

    # Write chat history in individual collapsible sections
with st.sidebar:
    st.markdown("## Chat History")
    st.text("")
    # for role, text in st.session_state['chat_history']:
    if submit and input_text:
        expander = st.expander(f"You: {input_text}", expanded=False)
        expander.write(response_history)

# Use st.sidebar to add content to the sidebar
st.sidebar.title('Advertisement')

# Add an example advertisement (you can replace this with your own)
# st.sidebar.markdown("Put your advertisement content here!")
st.sidebar.markdown('<img src="https://d1csarkz8obe9u.cloudfront.net/posterpreviews/water-sale-ad-design-template-3a77219913ffe39f1adf1782ea3268f0_screen.jpg?ts=1637046434" alt="Advertisement">', unsafe_allow_html=True)

# Add some styling
st.markdown(
    """
    <style>
    .stTextInput, .stButton {
        border-radius: 8px;
        padding: 8px;
        margin-bottom: 12px;
    }
    .stTextInput {
        box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton {
        color: red;
        font-weight: bold;
        cursor: pointer;
        transition: background-color 0.3s, color 0.3s;
        background-color: transparent;
        border-radius: 8px;
        padding: 6px 12px;
    }
    .stMarkdown {
        margin-top: 16px;
        margin-bottom: 8px;
    }
    .stSidebar {
        background-color: '#ADF5EF';
    }
    .css-1p9gthz {
        background-color: '#ADF5EF'; /* Change this color to your desired sidebar background color */
    }
    </style>
    """,
    unsafe_allow_html=True,
)
