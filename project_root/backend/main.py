import sys
import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import logging
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from fuzzywuzzy import fuzz
import shutil
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db.connection import create_connection
from backend.utils.insert_data import insert_into_database

# NLTK 데이터 다운로드 (최초 실행 시 한 번 필요)
nltk.download('stopwords')
nltk.download('wordnet')

app = FastAPI()

# CORS 설정
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    words = text.lower().split()
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return ' '.join(words)

def find_similar_sentences(query, documents, threshold=80):
    preprocessed_query = preprocess_text(query)
    matches = []
    for doc in documents:
        sentences = doc['content'].split('. ')
        for sentence in sentences:
            preprocessed_sentence = preprocess_text(sentence)
            if fuzz.partial_ratio(preprocessed_query, preprocessed_sentence) >= threshold:
                matches.append({
                    'id': doc['id'],
                    'title': doc['title'],
                    'content': sentence
                })
    return matches

def extract_text_from_pdf(file_path):
    document = fitz.open(file_path)
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    document.close()
    return text

@app.get("/search")
async def search_documents(query: str):
    logger.info(f"Received search request: {query}")
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT id, title, LEFT(content, 200) AS content FROM documents")
    documents = cursor.fetchall()
    
    similar_sentences = find_similar_sentences(query, documents)
    
    cursor.close()
    connection.close()
    return similar_sentences

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    if not os.path.exists('files'):
        os.makedirs('files')

    file_location = f"files/{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    file_extension = file.filename.split('.')[-1]
    
    if file_extension == 'pdf':
        text = extract_text_from_pdf(file_location)
    elif file_extension in ['ppt', 'pptx']:
        text = extract_text_from_ppt(file_location)
    elif file_extension in ['xlsx', 'xls']:
        text = extract_text_from_excel(file_location)
    elif file_extension == 'txt':
        with open(file_location, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        return {"error": "Unsupported file type"}

    insert_into_database(file.filename, text)
    return {"info": "File uploaded successfully"}

@app.get("/document/{document_id}")
async def get_document(document_id: int):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM documents WHERE id = %s", (document_id,))
    document = cursor.fetchone()
    cursor.close()
    connection.close()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@app.delete("/document/{document_id}")
async def delete_document(document_id: int):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = %s", (document_id,))
    document = cursor.fetchone()
    if not document:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete the file from the filesystem
    file_path = f"files/{document[1]}"  # Assuming the file name is in the second column
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete the record from the database
    cursor.execute("DELETE FROM documents WHERE id = %s", (document_id,))
    connection.commit()
    
    cursor.close()
    connection.close()
    return {"info": "Document deleted successfully"}
