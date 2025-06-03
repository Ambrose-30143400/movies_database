# movies_database
A Movie Database
A movie database is a structured collection of information related to movies, including details about the movies themselves (such as title, release year, genre, and ratings), as well as associated data about the people involved in their creation and performance, like directors, actors, and genres. The primary goal of a movie database is to store, organize, and retrieve relevant information in a way that allows users to easily search, browse, and analyze different aspects of the film industry. It can serve various purposes, including cataloging movies, tracking actors' and directors' careers, understanding film trends, or providing movie recommendations. The purpose of this research project was to design and implement a movie database system that enables users to view movies, browse through different genres, and watch movies online, similar to Netflix. 
![image](https://github.com/user-attachments/assets/c17525cf-7e01-43eb-8372-3c7010132c8e)
# Aim and Objectives of the Study
The aim is to create a RESTful API that exposes basic CRUD operations (Create, Read, Update, Delete) for managing movie records and related entities such as directors, actors, and genres. The API will provide endpoints for users to interact with the movie data, and the project will follow software engineering best practices to ensure maintainability, scalability, and readability. The objectives are listed thus
i.	Develop a RESTful API that facilitates efficient data management through CRUD operations for movies, actors, directors, and genres.
ii.	Design the Database Schema using PHPMyAdmin Database Environment 
iii.	Implement the backend of a movie management website, allowing users to interact with movie data through both the API and the web interface.
# Methodology of the Study
The methodology used for this study is Agile methodology. Agile is an iterative and incremental approach to software development. It emphasizes flexibility, collaboration, customer feedback, and rapid delivery of small, functional software increments. The project involves building small, manageable pieces of functionality (CRUD operations for movies, actors, directors, genres) in iterations. Each iteration can be seen as a small increment where specific functionality is added, tested, and deployed.
# Review of Related Literature
The creation of effective movie management systems has been a critical area of research, particularly regarding the storage, retrieval, and management of vast movie datasets. A significant contribution to this field comes from the Internet Movie Database (IMDb), which has set a precedent for how movie data is organized and accessed. Weible (2021) further examined the evolution of IMDb, discussing how such large-scale systems need to continually update their data to meet user expectations and handle increasing demands for new features, such as movie recommendations and actor biographical data. Weible's work emphasizes the importance of structured data models and efficient CRUD operations for movie data, making it highly relevant for building RESTful APIs that manage movie, actor, director, and genre records in a similar manner (Weible, 2021). In the domain of network analysis, researchers have been using graph theory to analyze the relationships between movies, actors, and directors. Brandes and Erlebach (2021) also expanded on the role of network analysis in movie-related data, particularly focusing on movie-actor relationships and actor biographies. They noted that by visualizing these relationships, users can explore the evolution of actors' careers and the movies they have been involved with. Integrating such features into a movie management API could allow users to query movies by actor, filter by collaborations, and explore actors' careers in greater depth (Brandes & Erlebach, 2021). Ahmed et al. (2021) presented a detailed study on affiliation networks, where they applied graph theory to understand how actors and directors are affiliated through various movies over time. This concept could be directly applied to the development of a movie management system by tracking movie collaborations and actor/actress participation in films, thus enabling richer search and filtering functionalities within the API (Ahmed et al., 2021).
# Software Requirements
1.	Python 3.10 and above
2.	Xampp
3.	Pycharm IDE Community Edition
Python Modules
i.	Flask
ii.	Haslib
iii. Mysql.connector

The app.py contain the render page of the HTML
The app2.py contain the API endpoint
# Justification of the use of the programming language (Python)
Python has been chosen as the programming language for developing the movie management system and the RESTful API for several compelling reasons. Python comes with a vast ecosystem of libraries and frameworks, which can significantly accelerate the development process. For this project, we will utilize libraries like Flask for web development and MySQL.connector for database management. These libraries have been designed to integrate easily, providing powerful features without requiring a steep learning curve. Python excels at integration with various other technologies, databases, and tools. In this project, Python will integrate seamlessly with
i.	MySQL for data storage and management of movie, actor, and director records.
ii.	XAMPP as a local development environment, providing the Apache web server and MySQL database to run the system locally before deployment.
iii.	Flask enables easy creation of RESTful APIs, which can be consumed by web browsers, mobile apps, or any other client that communicates via HTTP.
Justification for the Use of Flask Framework in the Movie Management System
The Flask framework has been selected for the development of the movie management system and its associated RESTful API for several important reasons. Flask is a micro-framework, meaning it provides only essential tools and features, allowing developers to build applications with minimal overhead. Flask provides excellent support for building RESTful APIs using Flask-RESTful or Flask-RESTX. Flask supports various database technologies, including SQLAlchemy for relational databases (e.g., MySQL, PostgreSQL) and NoSQL databases (e.g., MongoDB).
# app2.py
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

![image](https://github.com/user-attachments/assets/3a69b28f-0d41-4a4e-9c3f-1eb5bf9d81e5)

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

![image](https://github.com/user-attachments/assets/a71b42ad-c853-439b-8f89-49ed55a27b91)

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
![image](https://github.com/user-attachments/assets/089874f6-53fc-4b84-9dce-87253bb1d2ef)

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

# References
Auber, D., Chiricota, Y., Jourdan, F., & Melanon, G. (2020). Multiscale visualization of small world networks. Proceedings of InfoVis, 75-81.
Ahmed, A., Dwyer, T., Forster, M., Fu, X., Ho, J., Hong, S., Koschützki, D., Murray, C., Nikolov, N., Tarassov, A., Taib, R., & Xu, K. (2021). GEOMI: GEometry for Maximum Insight. Proceedings of Graph Drawing, 468-479.
Batagelj, V. (2022). Analysis of large networks - Islands. Dagstuhl seminar 03361: Algorithmic Aspects of Large and Complex Networks.
Brandes, U., & Erlebach, T. (2021). Network analysis: Methodological foundations. Springer.
Brandes, U., Hoefer, M., & Pich, C. (2020). Affiliation dynamics with an application to movie-actor biographies. Proceedings of EuroVis, 179-186.
Wasserman, S., & Faust, K. (2020). Social Network Analysis: Methods and Applications. Cambridge University Press.
Weible, C. (2021). The Internet Movie Database. Internet Reference Services Quarterly, 6(2), 47-50. https://doi.org/10.1300/J136v06n02_05
