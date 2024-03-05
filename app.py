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
        prompt_response.append(chunk.text)
    return "".join(prompt_response)  # Concatenate all parts of the response

# Function to update chat history in Google Spreadsheet
def update_chat_history(username, input_text, response, satisfaction):
    row = [username, input_text, response, satisfaction]
    sheet.append_row(row)

# Streamlit UI setup
st.set_page_config(page_title="Water Bot Demo", page_icon=":droplet:")

# Initialize session state variables if they don't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'current_response' not in st.session_state:
    st.session_state['current_response'] = ""

# Sidebar: User Registration and Chat History
with st.sidebar:
    st.title("User Registration")
    username_input = st.text_input("Enter your username:")
    if username_input:
        st.session_state['username'] = username_input

    # st.title("Chat History")
    # for item in st.session_state['chat_history']:
    #     st.text(f"User: {item[0]}")
    #     st.text(f"Question: {item[1]}")
    #     st.text(f"Response: {item[2]}")
    #     st.text(f"Satisfaction: {item[3]}")
    #     st.markdown("---")

# Main Page: Question Input and Response
st.title("Water Bot Chat Interface")
if 'username' in st.session_state and st.session_state['username']:
    input_text = st.text_input("Ask me any question:")
    generate_button = st.button("Get Response")

    if generate_button and input_text:
        # Get the response and store it in session state
        st.session_state['current_response'] = get_gemini_response(input_text)

    # Display the response if it's available
    try:
        if st.session_state['current_response']:
            st.write(st.session_state['current_response'])
    except:
        st.warning("Server busy, try after some time.")        

    # Select box for satisfaction
    satisfaction = st.selectbox(
        'How satisfied are you with the answer?',
        ('Very Satisfied', 'Satisfied', 'Somewhat satisfied', 'Not satisfied'),
        key="satisfaction_option"
    )

    # Save feedback button
    if st.button("Save Feedback"):
        if st.session_state['current_response'] and input_text:
            update_chat_history(st.session_state['username'], input_text, st.session_state['current_response'], satisfaction)
            st.success("Feedback saved successfully!")
            # Clear the response to prepare for the next interaction
            st.session_state['current_response'] = ""
else:
    st.info("Please enter a username in the sidebar to begin.")
