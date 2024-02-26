import http.server
import socketserver
import cgi
import os
import sys
from jinja2 import Environment, FileSystemLoader
import sqlite3
import webbrowser
import urllib.parse

# Set up Jinja2 environment
template_env = Environment(loader=FileSystemLoader(searchpath="./templates"))

# Database initialization
def init_db():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")

    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        );
    ''')
    print("Table created successfully")
    conn.close()


# Function to retrieve a user from the database by username
def get_user(username):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    conn.close()
    return user


# Handler for HTTP requests
class MyHandler(http.server.CGIHTTPRequestHandler):
           
    def do_GET(self):
        global user_id
        if self.path == '/':
            self.path = '/templates/login.html'
        elif self.path == '/dashboard':
            if user_id:
                template = template_env.get_template('dashboard.html')
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(template.render(user_id=user_id).encode('utf-8'))
                return
            else:
                self.send_response(301)
                self.send_header('Location','/')
                self.end_headers()
        elif self.path == '/logout':
            user_id = None
            self.send_response(301)
            self.send_header('Location', '/')
            self.end_headers()
        else:
           self.send_response(404)
           self.send_header('Content-type','text/plain')
           self.end_headers()
           self.wfile.write("404 Not Found".encode())
        return http.server.CGIHTTPRequestHandler.do_GET(self)


    def do_POST(self):
        global user_id
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
    
        if self.path == '/login':
            # Parse form data
            form_data = urllib.parse.parse_qs(post_data)
            username = form_data.get('username', [''])[0]
            password = form_data.get('password', [''])[0]
            
            # Check user credentials
            user = get_user(username)
            if user and user[2] == password:
                # set the user_id 
                user_id = user[1] # store user_id as global
                # Redirect to dashboard upon successful login
                self.send_response(302)
                self.send_header('Location', '/dashboard')
                self.end_headers()
                return
            else:
                # Render login page again if login fails
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                template = template_env.get_template('login.html')
                self.wfile.write(template.render().encode('utf-8'))


if __name__ == '__main__':
    init_db()
    # Create a simple server
    server = socketserver.TCPServer(('localhost', 8080), MyHandler)

    # Open web browser
    webbrowser.open('http://localhost:8080')

    # Serve requests
    server.serve_forever()
