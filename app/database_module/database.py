import sqlite3

def get_connection():
    conn = sqlite3.connect('app/database_module/chat_sessions.db')
    return conn

def create_tables():
    with get_connection() as conn:
        # Table for storing session info
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT UNIQUE
            )
        ''')

def save_session(session_name):
    with get_connection() as conn:
        cursor = conn.cursor()
        # Insert the session name if not already present
        cursor.execute('''
            INSERT INTO sessions (session_name) VALUES (?)
            ON CONFLICT(session_name) DO NOTHING
        ''', (session_name,))
        conn.commit()
        
        # Fetch the newly created session ID
        cursor.execute('SELECT id FROM sessions WHERE session_name = ?', (session_name,))
        session_id = cursor.fetchone()[0]
        
        # Create a new table for this session to store messages
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS session_{session_id} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT,
                bot_response TEXT
            )
        ''')
        conn.commit()

def save_message(session_name, user_message, bot_response):
    with get_connection() as conn:
        cursor = conn.cursor()
        # Get session ID
        cursor.execute('SELECT id FROM sessions WHERE session_name = ?', (session_name,))
        session_id = cursor.fetchone()
        if session_id:
            session_table = f"session_{session_id[0]}"
            cursor.execute(f'''
                INSERT INTO {session_table} (user_message, bot_response)
                VALUES (?, ?)
            ''', (user_message, bot_response))
            conn.commit()

def load_messages(session_name):
    with get_connection() as conn:
        cursor = conn.cursor()
        # Get session ID
        cursor.execute('SELECT id FROM sessions WHERE session_name = ?', (session_name,))
        session_id = cursor.fetchone()
        if session_id:
            session_table = f"session_{session_id[0]}"
            cursor.execute(f'SELECT user_message, bot_response FROM {session_table}')
            return cursor.fetchall()  # List of (user_message, bot_response)
        return []

def delete_session(session_name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM sessions WHERE session_name = ?', (session_name,))
        session_id = cursor.fetchone()
        if session_id:
            # Delete the associated message table
            cursor.execute(f'DROP TABLE IF EXISTS session_{session_id[0]}')
            # Delete the session record
            cursor.execute('DELETE FROM sessions WHERE session_name = ?', (session_name,))
            conn.commit()

def rename_session(old_session_name, new_session_name):
    with get_connection() as conn:
        cursor = conn.cursor()
        # Update the session name in the sessions table
        cursor.execute('UPDATE sessions SET session_name = ? WHERE session_name = ?', (new_session_name, old_session_name))
        conn.commit()

        # Rename the message table associated with this session
        cursor.execute('SELECT id FROM sessions WHERE session_name = ?', (new_session_name,))
        session_id = cursor.fetchone()[0]
        old_table = f"session_{session_id}"
        new_table = f"session_{session_id}"
        cursor.execute(f'ALTER TABLE {old_table} RENAME TO {new_table}')
        conn.commit()

def list_sessions():
    with get_connection() as conn:
        cursor = conn.execute('SELECT session_name FROM sessions ORDER BY id DESC')
        return [row[0] for row in cursor.fetchall()]

# Initialize the database and create tables
create_tables()
