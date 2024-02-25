import sqlite3

# Function to insert a user into the database
def insert_user(username, password):
    conn = sqlite3.connect('database.db')
    conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

# Function to check if a user exists in the database
def user_exists(username):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    conn.close()
    return user is not None

# Example usage:
username = 'samini'

if user_exists(username):
    print(f"User '{username}' exists in the database.")
else:
    print(f"User '{username}' does not exist in the database.")
    insert_user("samini","aaAA11!!")
