from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oidc import OpenIDConnect
import pyodbc

app = Flask(__name__)

# OIDC Configuration
app.config.update({
    'SECRET_KEY': 'FLASK_SECRET_KEY',  
    'OIDC_CLIENT_SECRETS': 'client_secret.json',  # Path to the JSON file
    'OIDC_RESOURCE_SERVER_ONLY': False,
    'OIDC_SCOPES': ['openid', 'profile', 'email'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
})

# Initialize OpenIDConnect
oidc = OpenIDConnect(app)

# Database and routes remain the same

# Database configuration
DB_SERVER = 'backendap1.database.windows.net'
DB_DATABASE = 'backend113'
DB_USERNAME = 'rashmi'
DB_PASSWORD = 'DB_PASSWORD'

def get_db_connection():
    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={DB_PASSWORD}')
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

@app.route('/')
def home():
    if oidc.user_loggedin:
        return f'Welcome {oidc.user_getfield("name")}!'
    else:
        return 'Welcome to the API Home Page! Please <a href="/login">log in</a>.'

@app.route('/login')
@oidc.require_login
def login():
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    oidc.logout()
    return redirect(url_for('home'))

@app.route('/data', methods=['GET'])
@oidc.require_login
def get_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM your_table_name')  # Adjust query as needed
        rows = cursor.fetchall()
        conn.close()
        
        result = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/data', methods=['POST'])
@oidc.require_login
def post_data():
    try:
        new_data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Adjust your INSERT query as needed
        cursor.execute(
            'INSERT INTO your_table_name (column1, column2) VALUES (?, ?)',
            new_data['column1'],
            new_data['column2']
        )
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
