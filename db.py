import sqlite3
import datetime

DB_NAME = 'bot_data.db'

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            start_date TIMESTAMP,
            last_activity TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            direction TEXT,
            text TEXT,
            date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def add_or_update_user(user_id, username, first_name, last_name):
    conn = get_db()
    c = conn.cursor()
    now = datetime.datetime.now()
    c.execute('SELECT id FROM users WHERE id = ?', (user_id,))
    if c.fetchone() is None:
        c.execute('INSERT INTO users (id, username, first_name, last_name, start_date, last_activity) VALUES (?, ?, ?, ?, ?, ?)',
                  (user_id, username, first_name, last_name, now, now))
    else:
        c.execute('UPDATE users SET last_activity = ?, username = ?, first_name = ?, last_name = ? WHERE id = ?',
                  (now, username, first_name, last_name, user_id))
    conn.commit()
    conn.close()

def log_message(user_id, direction, text):
    conn = get_db()
    c = conn.cursor()
    now = datetime.datetime.now()
    c.execute('INSERT INTO messages (user_id, direction, text, date) VALUES (?, ?, ?, ?)',
              (user_id, direction, text, now))
    conn.commit()
    conn.close()

def get_new_users_since(days=1):
    conn = get_db()
    c = conn.cursor()
    since = datetime.datetime.now() - datetime.timedelta(days=days)
    c.execute('SELECT COUNT(*) FROM users WHERE start_date >= ?', (since,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_inactive_users_since(days=1):
    """Пользователи, чья последняя активность была более days дней назад (условно ушедшие)"""
    conn = get_db()
    c = conn.cursor()
    since = datetime.datetime.now() - datetime.timedelta(days=days)
    c.execute('SELECT COUNT(*) FROM users WHERE last_activity < ?', (since,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_total_users():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    return count

def get_all_users():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, username, first_name, last_name, start_date, last_activity FROM users ORDER BY start_date DESC')
    users = c.fetchall()
    conn.close()
    return users

def get_user_messages(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT direction, text, date FROM messages WHERE user_id = ? ORDER BY date ASC', (user_id,))
    messages = c.fetchall()
    conn.close()
    return messages