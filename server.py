import http.server
import socketserver
import cgi
import os
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
        if self.path == '/':
            self.path = '/templates/login.html'
        elif self.path == '/dashboard':
            self.path = '/templates/dashboard.html'
        elif self.path == '/logout':
            self.path = '/templates/login.html'
        else:
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        return http.server.CGIHTTPRequestHandler.do_GET(self)


    def do_POST(self):
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
                # Redirect to dashboard upon successful login
                self.send_response(301)
                self.send_header('Location', '/dashboard')
                self.end_headers()
                # Pass user ID to dashboard template
                user_id = user[0] # Assuming user ID is the first column in the database
                template = template_env.get_template('dashboard.html')
                self.wfile.write(template.render(user_id=user_id).encode('utf-8'))
                return
            else:
                # Render login page again if login fails
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                template = template_env.get_template('login.html')
                self.wfile.write(template.render().encode('utf-8'))

        elif self.path == '/dashboard':
            # Get the username from the request headers or session data
            username = get_user(username)  # Replace this with actual username retrieval logic
            
            # Render dashboard with the username
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            template = template_env.get_template('dashboard.html')
            self.wfile.write(template.render(username=username).encode('utf-8'))
    
        else:
            # Return 404 for unknown paths
            self.send_error(404, 'File Not Found')



# Function to open web browser
def open_browser():
    webbrowser.open('http://localhost:8080')

# Main function
def main():
    init_db()
    
    # Create a simple server
    server = socketserver.TCPServer(('localhost', 8080), MyHandler)

    # Open web browser
    open_browser()

    # Serve requests
    server.serve_forever()

if __name__ == '__main__':
    main()
