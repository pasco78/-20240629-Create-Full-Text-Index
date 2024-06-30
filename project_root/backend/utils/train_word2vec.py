import os
from gensim.models import Word2Vec
from backend.db.connection import create_connection

def train_word2vec_model():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT content FROM documents")
    documents = cursor.fetchall()
    cursor.close()
    connection.close()

    sentences = [doc[0].split() for doc in documents]
    model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)
    model.save("word2vec.model")

if __name__ == "__main__":
    train_word2vec_model()

