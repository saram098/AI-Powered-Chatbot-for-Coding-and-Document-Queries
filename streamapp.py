import streamlit as st
import requests
import json
import os

# Constants for FastAPI endpoints
BASE_URL = "http://localhost:8002"

def save_chat_history(user_id, chat_id, history):
    user_folder = f'Data/{user_id}'
    os.makedirs(user_folder, exist_ok=True)
    chat_file = f'{user_folder}/{chat_id}'
    with open(chat_file, 'w') as f:
        json.dump(history, f, indent=4)

def load_chat_history(user_id, chat_id):
    user_folder = f'Data/{user_id}'
    chat_file = f'{user_folder}/{chat_id}'
    try:
        with open(chat_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def main():
    st.title("Chat Assistant")

    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
        st.session_state.chat_id = None
        st.session_state.chat_history = []

    # Ask for User ID
    if st.session_state.user_id is None:
        user_id = st.text_input("Enter your User ID:")
        if st.button("Submit"):
            if user_id:
                st.session_state.user_id = user_id
                st.session_state.chat_id = None
                st.session_state.chat_history = []
                st.experimental_rerun()
    else:
        user_id = st.session_state.user_id

        # Ensure user folder exists
        user_folder = f'Data/{user_id}'
        os.makedirs(user_folder, exist_ok=True)

        # Sidebar with New Chat option and Past Chats dropdown
        with st.sidebar:
            st.write(f"User: {user_id}")

            # Dropdown for Past Chats
            past_chats = [f for f in os.listdir(user_folder) if f.endswith('.json')]
            selected_chat = st.selectbox("Past Chats", options=["Select a chat"] + past_chats)
            if selected_chat != "Select a chat":
                st.session_state.chat_id = selected_chat
                st.session_state.chat_history = load_chat_history(user_id, selected_chat)

            if st.button("New Chat"):
                st.session_state.chat_id = None
                st.session_state.chat_history = []

        # Generate chat ID if not exists
        if st.session_state.chat_id is None:
            chat_id = f"chat_{len([f for f in os.listdir(user_folder) if f.endswith('.json')]) + 1}.json"
            st.session_state.chat_id = chat_id
        else:
            chat_id = st.session_state.chat_id

        # Load chat history
        chat_history = st.session_state.chat_history

        # Display chat history
        for entry in chat_history:
            with st.chat_message('user'):
                st.markdown(entry['prompt'])
            with st.chat_message('assistant', avatar='✨'):
                st.markdown(entry['response'])

        # Input handling
        input_type = st.selectbox("Select input type", ["Text", "Document", "Audio"])

        if input_type == "Text":
            if prompt := st.chat_input('Your message here...'):
                with st.chat_message('user'):
                    st.markdown(prompt)

                response = requests.post(f"{BASE_URL}/query", json={
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "question": prompt
                })
                answer = response.json().get("answer")

                st.session_state.chat_history.append({'prompt': prompt, 'response': answer})
                save_chat_history(user_id, chat_id, st.session_state.chat_history)
                st.experimental_rerun()
                
        elif input_type == "Document":
            uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])
            question = st.text_input("Ask a question based on the document:")
            if st.button("Submit"):
                if uploaded_file and question:
                    files = {'file': uploaded_file.getvalue()}
                    data = {'user_id': user_id, 'chat_id': chat_id, 'question': question}
                    response = requests.post(f"{BASE_URL}/query_document", files=files, data=data)
                    answer = response.json().get("answer")

                    st.session_state.chat_history.append({'prompt': f"Document: {uploaded_file.name}, Question: {question}", 'response': answer})
                    save_chat_history(user_id, chat_id, st.session_state.chat_history)

        elif input_type == "Audio":
            uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3"])
            if st.button("Submit"):
                if uploaded_file:
                    files = {'file': uploaded_file.getvalue()}
                    data = {'user_id': user_id, 'chat_id': chat_id}
                    response = requests.post(f"{BASE_URL}/query_audio", files=files, data=data)
                    answer = response.json().get("answer")

                    st.session_state.chat_history.append({'prompt': "Audio file uploaded", 'response': answer})
                    save_chat_history(user_id, chat_id, st.session_state.chat_history)

if __name__ == "__main__":
    main()
