import mysql.connector

def create_connection():
    return mysql.connector.connect(
       host="localhost",
        user="root",
        password="lge123",
        database="database"
    )
