# AI-Powered Chatbot for Coding and Document Queries

## Overview
This project consists of two main components:
- **FastAPI Backend**: Handles text, document (PDF), and audio queries using the Groq API for coding and document-based queries.
- **Streamlit Frontend**: Provides an intuitive chat interface for users to interact with the system by entering text, uploading documents, or audio queries.

The chatbot processes user inputs and generates relevant answers using a language model. You can customize the backend to integrate different models for various tasks.

## Features
- **Text Queries**: Users can ask questions directly in text format.
- **Document Queries**: Upload PDFs and ask questions based on the document content.
- **Audio Queries**: Upload audio files, which are transcribed and used for generating responses.
- **Chat History**: Automatically saves per user in the `chats` folder for future reference.

## Setup Instructions

### 1. Clone the Repository
First, clone the project repository and navigate into the project directory:
```bash
git clone https://github.com/your-repository/AI-Powered-Chatbot-for-Coding-and-Document-Queries.git
cd AI-Powered-Chatbot-for-Coding-and-Document-Queries
```
### 2. Install Dependencies
Install the necessary packages by running:
```bash
pip install -r requirements.txt
```
This will install:

- FastAPI: Backend framework.
- Uvicorn: ASGI server for FastAPI.
- Streamlit: Interactive frontend.
- PyMuPDF: PDF handling.
- SpeechRecognition and pydub: Audio processing.
- Groq API: For using Groq hardware and models.

### 3. Set Up Environment Variables
Create a ```.env``` file in the root directory to store sensitive information such as API keys and URLs. Use the following template for the ```.env``` file:
```bash
BASE_URL=http://127.0.0.1:8002
GROQ_API_KEY=your_groq_api_key_here
```
Replace ```your_groq_api_key_here``` with your Groq API key. You can obtain the API key by registering on the Groq platform.

### 4. Run the FastAPI Backend
Start the FastAPI backend by running:
```python app.py```
This will start the FastAPI server and provide a local URL, typically ```http://127.0.0.1:8002```. Add this URL to your ```.env``` file as the ```BASE_URL```.

##Note: The application automatically creates the following directories:

- Data Folder: Stores user-uploaded files (PDFs, audio).
- Chats Folder: Saves user-specific chat histories in JSON format.
###5. Run the Streamlit Frontend
After the FastAPI backend is running, open a new terminal and run the Streamlit frontend:

```bash
streamlit run streamapp.py
```
This will provide a link (typically ```http://localhost:8501```) to access the chat interface in your browser. The frontend interacts with the FastAPI backend to process queries and display chat history.

###6. Workflow Summary
- Run the backend (```app.py```) to obtain the localhost URL (e.g., ```http://127.0.0.1:8002```).
- Add this URL to the ```.env``` file under the ```BASE_URL```.
- Run the frontend (```streamapp.py```) and use the provided URL for checking, testing, or production.
###7. Changing the Model
You can change the model used in the backend by modifying the following code in the app.py file:

```
def query_groq(messages):
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama3-8b-8192",  # Change the model here
    )
    return chat_completion.choices[0].message.content
```
To modify the model:

- Navigate to the function ```query_groq()``` in ```app.py```.
- Replace ```"llama3-8b-8192"``` with any other model name supported by the Groq API.
##Note: You can find a list of available models on the Groq website. Be sure to also update the GROQ_API_KEY in your .env file if necessary.

###Folder Structure
```bash
app.py                 # FastAPI application handling text, document, and audio queries
streamapp.py           # Streamlit app providing the frontend chat interface
chats/{user_id}        # Stores chat history per user, with each session saved as a separate JSON file
data/                  # Stores user-uploaded PDFs and audio files
```
###Usage
- Navigate to the Streamlit app link in your browser.
- Enter your user ID to start a new chat or continue a previous session.
- Submit queries in one of the following forms:
- Text: Directly type your questions.
- Document (PDF): Upload a document and ask questions based on the content.
- Audio: Upload an audio file, and the system will transcribe and respond.

