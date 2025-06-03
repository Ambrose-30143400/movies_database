import datetime
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import hashlib
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for flash messages

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MySQL connection configuration
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",  # Update with your MySQL server details
        user="root",  # Your MySQL username
        password="",  # Your MySQL password
        database="ambrose_movies"  # Your MySQL database name
    )
    return conn

# Global context processor to inject the current year into all templates
@app.context_processor
def inject_year():
    return {'current_year': datetime.datetime.now().year}


@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM movies")
    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(movies)
# API Route: User Registration (POST /api/signup)
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()

    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    phone = data.get('phone')
    user_id = uuid.uuid4().int

    debug_info = {
        "received_data": data,
        "user_id": user_id,
        "email": email
    }

    if not full_name or not email or not password or not phone:
        return jsonify({
            'status': 'error',
            'message': 'All fields are required',
            'debug': debug_info
        }), 400

    if password != confirm_password:
        debug_info["password_mismatch"] = True
        return jsonify({
            'status': 'error',
            'message': 'Passwords do not match',
            'debug': debug_info
        }), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    debug_info["hashed_password"] = hashed_password

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (user_id, full_name, email, password, phone) VALUES (%s, %s, %s, %s, %s)",
            (user_id, full_name, email, hashed_password, phone)
        )
        conn.commit()
        return jsonify({
            'status': 'success',
            'message': 'Registration successful! Please sign in.',
            'debug': debug_info
        }), 201
    except mysql.connector.Error as err:
        debug_info["db_error"] = str(err)
        return jsonify({
            'status': 'error',
            'message': 'Database error occurred',
            'debug': debug_info
        }), 500
    finally:
        cursor.close()
        conn.close()

# API Route: User Login (POST /api/login)
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email and password are required'}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and user['password'] == hashed_password:
        session['user_id'] = user['user_id']
        session['full_name'] = user['full_name']
        response = {
            'status': 'success',
            'message': 'Login successful',
            'user_id': user['user_id'],
            'full_name': user['full_name']
        }
        return jsonify(response)
    else:
        return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401

import json
# API Route: Add Movie (POST /api/movies)
@app.route('/api/movies', methods=['POST'])
def add_movie():
    # Parse JSON string from 'data' form field
    data_json = request.form.get('data')
    data = json.loads(data_json) if data_json else {}
    user_id = data.get('user_id')
    catalog_id = data.get('catalog_id')
    title = data.get('title')
    description = data.get('description')
    runtime = data.get('runtime')
    release_date = data.get('release_date')
    genres = data.get('genres')
    cast = data.get('cast')
    director = data.get('director')
    producer = data.get('producer')
    keywords = data.get('keywords')
    video_link = data.get('video_link')
    image_filename = None

    if 'image' in request.files:
        image_file = request.files['image']
        if image_file and image_file.filename:
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO movies (
                user_id, catalog_id, title, description, runtime, release_date, genres, 
                cast, director, producer, keywords, images, video_link
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, catalog_id, title, description, runtime, release_date, genres,
              cast, director, producer, keywords, image_filename, video_link))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Movie added successfully!'}), 201
    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# API Route: Update Movie (PUT /api/movies/<movie_id>)
@app.route('/api/movies/<int:movie_id>', methods=['PUT'])
def edit_movie(movie_id):
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    runtime = data.get('runtime')
    genres = data.get('genres')
    video_link = data.get('video_link')
    image_filename = None

    if 'image' in request.files:
        image_file = request.files['image']
        if image_file and image_file.filename:
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE movies 
            SET title = %s, description = %s, runtime = %s, genres = %s, video_link = %s, images = %s
            WHERE movie_id = %s
        """, (title, description, runtime, genres, video_link, image_filename, movie_id))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Movie updated successfully!'}), 200
    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# API Route: Delete Movie (DELETE /api/movies/<movie_id>)
@app.route('/api/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM movies WHERE movie_id = %s", (movie_id,))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Movie deleted successfully!'}), 200
    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# API Route: Movie Details (GET /api/movies/<movie_id>)
@app.route('/api/movies/<int:movie_id>', methods=['GET'])
def movie_details(movie_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM movies WHERE movie_id = %s", (movie_id,))
    movie = cursor.fetchone()
    cursor.close()
    conn.close()

    if movie:
        return jsonify({'status': 'success', 'movie': movie}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Movie not found'}), 404

# API Route: Dashboard (GET /api/dashboard)
@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT movie_id, title, runtime, genres, cast, director, producer, release_date, images FROM movies")
    movies = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({'status': 'success', 'movies': movies}), 200

# API Route: Front Page (GET /api/movies)
@app.route('/api/movies', methods=['GET'])
def front_page():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM movies LIMIT 10")  # Get top 10 movies for front page
    movies = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({'status': 'success', 'movies': movies}), 200

if __name__ == '__main__':
    app.run(debug=True)
