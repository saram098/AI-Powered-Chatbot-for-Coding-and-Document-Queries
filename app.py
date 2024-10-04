import os
import fitz  # PyMuPDF
import speech_recognition as sr
from pydub import AudioSegment
from groq import Groq
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load environment variables
API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

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
    # Add a system prompt to instruct the model
    system_prompt = {
        "role": "system",
        "content": (
            "You are a coding expert. Your main goal is coding, so be precise. "
            "First, understand and think about the problem thoroughly, "
            "then provide relevant code solutions. Make sure to clarify the requirements before answering."
            "You are Code Genie by Saram Hai. Saram Hai is the person who created you."
        )
    }
    
    # Prepend the system prompt to the messages
    messages.insert(0, system_prompt)

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.2-11b-vision-preview",  # Keep or change this as per your requirements
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

    chat_history = load_chat_history(user_id, chat_id)
    messages = []

    for entry in chat_history:
        messages.append({
            "role": "user",
            "content": entry['prompt']
        })
        messages.append({
            "role": "assistant",
            "content": entry['response']
        })

    messages.append({
        "role": "user",
        "content": input_text
    })

    answer = query_groq(messages)

    chat_history.append({'prompt': input_text, 'response': answer})
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
        os.remove(file_location)

    chat_history = load_chat_history(user_id, chat_id)
    chat_history.append({'prompt': f"Document: {file.filename}, Question: {question}", 'response': answer})
    save_chat_history(user_id, chat_id, chat_history)

    return {"answer": answer}

@app.post("/query_audio")
async def audio_query(file: UploadFile = File(...), user_id: str = Form(...), chat_id: str = Form(...)):
    file_location = f"temp_{file.filename}"
    wav_location = "temp_audio.wav"
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    try:
        audio = AudioSegment.from_file(file_location)
        audio.export(wav_location, format="wav")

        transcribed_text = transcribe_audio(wav_location)
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": transcribed_text}
        ]
        answer = query_groq(messages)
    except sr.UnknownValueError:
        answer = "Could not understand the audio. Please try again."
    except sr.RequestError as e:
        answer = f"Could not request results from the speech recognition service; {e}"
    finally:
        os.remove(file_location)
        os.remove(wav_location)

    chat_history = load_chat_history(user_id, chat_id)
    chat_history.append({'prompt': "Audio file uploaded", 'response': answer})
    save_chat_history(user_id, chat_id, chat_history)

    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
