import datetime
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, session
import hashlib
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
print(app)
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
    cursor.execute("SELECT * FROM movies")  # Adjust based on your actual table structure
    movies = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('index.html', movies=movies)


# Route: Add Movie
@app.route('/add_movie', methods=['POST'])
def add_movie():
    user_id = request.form['user_id']
    catalog_id = request.form['catalog_id']
    title = request.form['title']
    description = request.form['description']
    runtime = int(request.form['runtime'])  # Convert to int if needed
    release_date = request.form['release_date']
    genres = request.form['genres']
    cast = request.form['cast']
    director = request.form['director']
    producer = request.form['producer']
    keywords = request.form['keywords']
    video_link = request.form['video_link']

    # Handle image upload
    image_filename = None  # Default to None if no image is uploaded
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file and image_file.filename:
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)  # Save image to upload folder

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO movies (
            user_id, catalog_id, title, description, runtime, release_date, genres, 
            cast, director, producer, keywords, images, video_link
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (user_id, catalog_id, title, description, runtime, release_date, genres,
          cast, director, producer, keywords, image_filename, video_link))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Movie added successfully!', 'success')
    return redirect(url_for('dashboard'))

# Route: Movie Details
@app.route('/details/<int:movie_id>', methods=['GET'])
def movie_details(movie_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM movies WHERE movie_id = %s", (movie_id,))
    movie = cursor.fetchone()
    cursor.close()
    conn.close()

    if not movie:
        flash("Movie not found", "error")
        return redirect(url_for('dashboard'))

    return render_template('details.html', movie=movie)

# Route: Edit Movie
@app.route('/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        rating = request.form['rating']
        genres = request.form['genres']
        video_link = request.form['video_link']
        image = request.files['image']

        filename = None
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cursor.execute("""
            UPDATE movies 
            SET title = %s, description = %s, rating = %s, genres = %s, video_link = %s, images = %s
            WHERE id = %s
        """, (title, description, rating, genres, video_link, filename, movie_id))
        conn.commit()
        flash('Movie updated successfully', 'success')
        return redirect(url_for('movie_details', movie_id=movie_id))

    cursor.execute("SELECT * FROM movies WHERE movie_id = %s", (movie_id,))
    movie = cursor.fetchone()
    cursor.close()
    conn.close()

    if movie:
        return render_template('edit_movie.html', movie=movie)
    else:
        flash('Movie not found', 'error')
        return redirect(url_for('dashboard'))

# Route: Delete Movie
@app.route('/delete/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE movie_id = %s", (movie_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Movie deleted successfully', 'success')
    return redirect(url_for('dashboard'))

# Route: Dashboard
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')  # Retrieves the value of 'user_id'
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT movie_id, title, runtime, genres, cast, director, producer, release_date, images FROM movies")
    movies = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('dashboard.html', movies=movies, user_id=user_id)

# Route: Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        phone = request.form['phone']
        user_id = uuid.uuid4().int  # Generates a large unique number

        if not full_name or not email or not password or not phone:
            flash('All fields are required!', 'error')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('signup'))

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (user_id, full_name, email, password, phone) VALUES (%s, %s, %s, %s, %s)",
                (user_id, full_name, email, hashed_password, phone)
            )
            conn.commit()
            flash('Registration successful! Please sign in.', 'success')
            return redirect(url_for('signup'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'error')
        finally:
            cursor.close()
            conn.close()

    return render_template('signup.html')

# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            flash('Both email and password are required!', 'error')
            return redirect(url_for('login'))

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and user['password'] == hashed_password:
            session['user_id'] = user['user_id']
            session['full_name'] = user['full_name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')

        cursor.close()
        conn.close()

    return render_template('signin.html')

if __name__ == '__main__':
    app.run(debug=True)
