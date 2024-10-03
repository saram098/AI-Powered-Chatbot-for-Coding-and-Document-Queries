import os
import fitz  # PyMuPDF
import speech_recognition as sr
from pydub import AudioSegment
from groq import Groq
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json

client = Groq(api_key="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")

app = FastAPI()

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextQuery(BaseModel):
    user_id: str
    chat_id: str
    question: str

def query_groq(messages):
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama3-8b-8192",
    )
    
    return chat_completion.choices[0].message.content

def query_from_document(pdf_path, question):
    with fitz.open(pdf_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant who answers questions based on the provided document.",
        },
        {
            "role": "user",
            "content": f"The document content is:\n{text}\n\nNow answer this question based on the document: {question}"
        }
    ]
    return query_groq(messages)

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio)

def load_chat_history(user_id, chat_id):
    """Load chat history from a JSON file."""
    chat_file = f'chats/{user_id}/{chat_id}.json'
    try:
        with open(chat_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_chat_history(user_id, chat_id, history):
    """Save chat history to a JSON file."""
    user_folder = f'chats/{user_id}'
    os.makedirs(user_folder, exist_ok=True)
    chat_file = f'{user_folder}/{chat_id}.json'
    with open(chat_file, 'w') as f:
        json.dump(history, f, indent=4)

@app.post("/query")
async def text_query(query: TextQuery):
    user_id = query.user_id
    chat_id = query.chat_id
    input_text = query.question

    # Load chat history for the given user ID and chat ID
    chat_history = load_chat_history(user_id, chat_id)

    # Prepare messages for Groq API with chat history
    messages = []

    # Include previous chat history in the messages
    for entry in chat_history:
        messages.append({
            "role": "user",
            "content": entry['prompt']
        })
        messages.append({
            "role": "assistant",
            "content": entry['response']
        })

    # Add the new user input to the messages
    messages.append({
        "role": "user",
        "content": input_text
    })

    # Get response from Groq API
    answer = query_groq(messages)

    # Add user input and LLM result to history
    chat_history.append({'prompt': input_text, 'response': answer})

    # Save chat history back to the JSON file
    save_chat_history(user_id, chat_id, chat_history)

    return {"answer": answer}

@app.post("/query_document")
async def document_query(file: UploadFile = File(...), user_id: str = Form(...), chat_id: str = Form(...), question: str = Form(...)):
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    try:
        answer = query_from_document(file_location, question)
    finally:
        os.remove(file_location)  # Clean up the temporary file

    # Load chat history for the given user ID and chat ID
    chat_history = load_chat_history(user_id, chat_id)

    # Add user input and LLM result to history
    chat_history.append({'prompt': f"Document: {file.filename}, Question: {question}", 'response': answer})

    # Save chat history back to the JSON file
    save_chat_history(user_id, chat_id, chat_history)

    return {"answer": answer}

@app.post("/query_audio")
async def audio_query(file: UploadFile = File(...), user_id: str = Form(...), chat_id: str = Form(...)):
    file_location = f"temp_{file.filename}"
    wav_location = "temp_audio.wav"
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    try:
        # Convert to WAV format
        audio = AudioSegment.from_file(file_location)
        audio.export(wav_location, format="wav")

        # Transcribe the WAV audio
        transcribed_text = transcribe_audio(wav_location)
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {
                "role": "user",
                "content": transcribed_text
            }
        ]
        answer = query_groq(messages)
    except sr.UnknownValueError:
        answer = "Could not understand the audio. Please try again."
    except sr.RequestError as e:
        answer = f"Could not request results from the speech recognition service; {e}"
    finally:
        try:
            os.remove(file_location)  # Clean up the temporary file
        except PermissionError:
            pass  # Handle or log if the file is still in use
        try:
            os.remove(wav_location)  # Clean up the temporary WAV file
        except PermissionError:
            pass  # Handle or log if the file is still in use

    # Load chat history for the given user ID and chat ID
    chat_history = load_chat_history(user_id, chat_id)

    # Add user input and LLM result to history
    chat_history.append({'prompt': "Audio file uploaded", 'response': answer})

    # Save chat history back to the JSON file
    save_chat_history(user_id, chat_id, chat_history)

    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
