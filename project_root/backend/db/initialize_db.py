from backend.db.connection import create_connection

def initialize_database():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS documents (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255),
        content TEXT,
        FULLTEXT (title, content)
    )''')
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    initialize_database()
