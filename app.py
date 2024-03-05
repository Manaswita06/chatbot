from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables
load_dotenv()

# Configure Google API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize GenerativeModel
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Function to connect to Google Sheets
def connect_to_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client

# Establish connection to Google Sheets
client = connect_to_google_sheets()
spreadsheet = client.open("Water related queries")
sheet = spreadsheet.worksheet("Water_related_queries")

# Function to get Gemini response
def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    prompt_response = []
    for chunk in response:
        st.write(chunk.text)
        prompt_response.append(chunk.text)
    return prompt_response    

# Function to update chat history in Google Spreadsheet
def update_chat_history(username, input_text, response, satisfaction):
    row = [username, input_text, ''.join(response), satisfaction]
    sheet.append_row(row)

# Streamlit UI
st.set_page_config(page_title="Water Bot Demo", page_icon=":droplet:")

# Initialize chat_history in session state if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Sidebar: User Registration and Chat History
with st.sidebar:
    st.title("User Registration")
    username_input = st.text_input("Enter your username:")
    if username_input:
        st.session_state['username'] = username_input

    st.title("Chat History")
    for item in st.session_state['chat_history']:
        if len(item) == 4:  # Ensure the tuple has four elements
            st.text(f"User: {item[0]}")
            st.text(f"Question: {item[1]}")
            st.text(f"Response: {''.join(item[2])}")  # Assuming item[2] is a list or similar iterable
            st.text(f"Satisfaction: {item[3]}")
            st.markdown("---")

# Main Page: Question Input and Response
st.title("Water Bot Chat Interface")
if 'username' in st.session_state and st.session_state['username']:
    input_text = st.text_input("Ask me any question:")
    if input_text:
        with st.spinner('Getting your response...'):
            response = get_gemini_response(input_text)
            st.session_state['chat_history'].append((st.session_state['username'], input_text, response))
            satisfaction = st.selectbox(
                'How satisfied are you with the answer?',
                ('Very Satisfied', 'Satisfied', 'Somewhat satisfied', 'Not satisfied'),
                key="satisfaction_option"
            )
            if st.button("Save Feedback"):
                update_chat_history(st.session_state['username'], input_text, response, satisfaction)
else:
    st.info("Please enter a username in the sidebar to begin.")
