import sqlite3

DB_NAME = "chatbot.db"


# Step 1: Connect to SQLite
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Step 2: Create database tables
def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (chat_id)
                REFERENCES conversations(id)
                ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# Step 3: Save a new conversation
def save_conversation(chat_id, title):

    conn = get_connection()

    conn.execute(
        "INSERT INTO conversations (id, title) VALUES (?, ?)",
        (chat_id, title)
    )

    conn.commit()
    conn.close()


# Step 4: Save a message
def save_message(chat_id, role, content):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO messages (chat_id, role, content)
        VALUES (?, ?, ?)
        """,
        (chat_id, role, content)
    )

    conn.commit()
    conn.close()


# Step 5: Load all conversations
def load_conversations():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title FROM conversations")
    rows = cursor.fetchall()

    conversations = {}

    for chat_id, title in rows:

        cursor.execute(
            """
            SELECT role, content
            FROM messages
            WHERE chat_id = ?
            ORDER BY id
            """,
            (chat_id,)
        )

        messages = [
            {"role": role, "content": content}
            for role, content in cursor.fetchall()
        ]

        conversations[chat_id] = {
            "title": title,
            "messages": messages
        }

    conn.close()

    return conversations


# Step 6: Update conversation title
def update_conversation_title(chat_id, title):

    conn = get_connection()

    conn.execute(
        "UPDATE conversations SET title = ? WHERE id = ?",
        (title, chat_id)
    )

    conn.commit()
    conn.close()


# Step 7: Delete conversation
def delete_conversation(chat_id):

    conn = get_connection()

    conn.execute(
        "DELETE FROM conversations WHERE id = ?",
        (chat_id,)
    )

    conn.commit()
    conn.close()