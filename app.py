# Import necessary libraries
from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
import time
import streamlit.components.v1 as components
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Load environment variables
load_dotenv()

# Configure Google API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize GenerativeModel
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def connect_to_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client

client = connect_to_google_sheets()
spreadsheet = client.open("Water related queries")
sheet = spreadsheet.worksheet("Water_related_queries")


# Function to get Gemini response with a typewriter effect
def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    prompt_response = []
    for chunk in response:
        st.write(chunk.text, type="default")   
        prompt_response.append(chunk.text)
    return prompt_response    


# Function to update chat history in Google Spreadsheet
def update_chat_history(username, input_text, response):
    row = [username, input_text, str(response)]
    sheet.append_row(row)

# Set page configuration
st.set_page_config(page_title="Water Bot Demo", page_icon=":droplet:")

# Define header and title
st.title("Water Bot Chat Interface")
st.markdown("---")

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
   
username_input = None   
with st.form("user_signup_form"):
    username_input = st.text_input("Enter your username:", key="user_input")
    submitted = st.form_submit_button("Submit")
    if submitted and username_input:
        st.session_state['username'] = username_input
    elif submitted and not username_input:
        st.error("Please enter a username!")

# required_chat_history = df[df['Name'] == username_input][['Name', 'Questions']]        

submit = ''
if username_input:
    st.subheader('Ask me any question')
    input_text = st.text_input("", key="input")
    submit = st.button("Enter", key="submit_button")
    
# Process user input and get response
response = ''
option = ''
if submit and input_text and username_input:
    st.subheader(f'You: {input_text}')
    # Placeholder for the response generation logic
    # Assuming response is the text response from the bot
    response = get_gemini_response(input_text)  # Replace with actual response generation logic
    st.session_state['chat_history'].append((username_input, input_text, response))
    option = st.selectbox(
        'How satisfied are you with the answer?',
        ('Very Satisfied', 'Satisfied', 'Somewhat satisfied', 'Answer not relevant to the topic'),
        index=None,
        placeholder='Select one option',
        key="satisfaction_option"
    )
    update_chat_history(username_input, input_text, response)
    
    if st.session_state.satisfaction_option:
        st.write(st.session_state.satisfaction_option)
        

elif submit and not input_text:
    st.error("Please enter a question!")
elif submit and not username_input:
    st.error("Please sign up to start chatting!")

# Chat history in the sidebar
with st.sidebar:
    st.markdown("## Chat History")
    if username_input:
        for role, text, response in st.session_state['chat_history']:
            expander = st.expander(f"{role}: {text}", expanded=False)
            expander.write(response)

    # Advertisement in the sidebar
# st.sidebar.title('Advertisement')
# st.sidebar.image("https://d1csarkz8obe9u.cloudfront.net/posterpreviews/water-sale-ad-design-template-3a77219913ffe39f1adf1782ea3268f0_screen.jpg?ts=1637046434", caption="Advertisement")

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