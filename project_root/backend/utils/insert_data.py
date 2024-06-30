import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.db.connection import create_connection

def insert_into_database(file_name, content):
    connection = create_connection()
    cursor = connection.cursor()
    sql_query = "INSERT INTO documents (title, content) VALUES (%s, %s)"
    cursor.execute(sql_query, (file_name, content))
    connection.commit()
    cursor.close()
    connection.close()
