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

