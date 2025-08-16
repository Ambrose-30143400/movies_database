import datetime
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import hashlib
from werkzeug.utils import secure_filename
import os
import uuid
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============   
# REUSABLE COMPONENTS
# ============   

class DatabaseManager:
    """Reusable database connection manager"""
    
    @staticmethod
    def get_connection():
        """Get database connection"""
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="ambrose_movies"
            )
            return conn
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            return None

    @staticmethod
    def execute_query(query, params=None, fetch_one=False, fetch_all=False):
        """Execute database query with error handling"""
        conn = DatabaseManager.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.rowcount
                
            return result
        except mysql.connector.Error as err:
            print(f"Query execution error: {err}")
            return None
        finally:
            cursor.close()
            conn.close()

class ResponseHelper:
    """Reusable response helper"""
    
    @staticmethod
    def success_response(message, data=None, status_code=200):
        """Generate success response"""
        response = {
            'status': 'success',
            'message': message,
            'timestamp': datetime.datetime.now().isoformat()
        }
        if data:
            response['data'] = data
        return jsonify(response), status_code

    @staticmethod
    def error_response(message, error_code=None, status_code=400):
        """Generate error response"""
        response = {
            'status': 'error',
            'message': message,
            'timestamp': datetime.datetime.now().isoformat()
        }
        if error_code:
            response['error_code'] = error_code
        return jsonify(response), status_code

class ValidationHelper:
    """Reusable validation helper"""
    
    @staticmethod
    def validate_required_fields(data, required_fields):
        """Validate required fields in data"""
        missing_fields = []
        for field in required_fields:
            if not data.get(field):
                missing_fields.append(field)
        return missing_fields

    @staticmethod
    def validate_email(email):
        """Basic email validation"""
        return '@' in email and '.' in email

class FileHelper:
    """Reusable file handling helper"""
    
    @staticmethod
    def save_uploaded_file(file, upload_folder):
        """Save uploaded file securely"""
        if file and file.filename:
            filename = secure_filename(file.filename)
            # Add timestamp to avoid conflicts
            timestamp = str(int(datetime.datetime.now().timestamp()))
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            return filename
        return None

# ============   
# DECORATORS
# ============   

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return ResponseHelper.error_response('Authentication required', 'AUTH_REQUIRED', 401)
        return f(*args, **kwargs)
    return decorated_function

def require_json(f):
    """Decorator to require JSON content type"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json and request.method in ['POST', 'PUT', 'PATCH']:
            return ResponseHelper.error_response('Content-Type must be application/json', 'INVALID_CONTENT_TYPE', 400)
        return f(*args, **kwargs)
    return decorated_function

# ============
# CONTEXT PROCESSORS
# ============

@app.context_processor
def inject_year():
    """Global context processor to inject current year"""
    return {'current_year': datetime.datetime.now().year}

# ============   
# API v1 ENDPOINTS
# ============   

# Test endpoint for API health check
@app.route('/api/v1/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    return ResponseHelper.success_response('API is healthy', {
        'version': '1.0',
        'timestamp': datetime.datetime.now().isoformat()
    })

# Test endpoint for user registration
@app.route('/api/v1/auth/register', methods=['POST'])
@require_json
def register_user():
    """
    Register a new user
    
    Test with curl:
    curl -X POST http://localhost:5000/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"full_name":"John Doe","email":"john@example.com","password":"password123","confirm_password":"password123","phone":"1234567890"}'
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['full_name', 'email', 'password', 'confirm_password', 'phone']
    missing_fields = ValidationHelper.validate_required_fields(data, required_fields)
    
    if missing_fields:
        return ResponseHelper.error_response(f'Missing required fields: {", ".join(missing_fields)}', 'MISSING_FIELDS')
    
    # Validate email format
    if not ValidationHelper.validate_email(data['email']):
        return ResponseHelper.error_response('Invalid email format', 'INVALID_EMAIL')
    
    # Validate password confirmation
    if data['password'] != data['confirm_password']:
        return ResponseHelper.error_response('Passwords do not match', 'PASSWORD_MISMATCH')
    
    # Check if user already exists
    existing_user = DatabaseManager.execute_query(
        "SELECT email FROM users WHERE email = %s",
        (data['email'],),
        fetch_one=True
    )
    
    if existing_user:
        return ResponseHelper.error_response('User with this email already exists', 'USER_EXISTS', 409)
    
    # Create new user
    user_id = uuid.uuid4().int
    hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
    
    result = DatabaseManager.execute_query(
        "INSERT INTO users (user_id, full_name, email, password, phone) VALUES (%s, %s, %s, %s, %s)",
        (user_id, data['full_name'], data['email'], hashed_password, data['phone'])
    )
    
    if result:
        return ResponseHelper.success_response('User registered successfully', {
            'user_id': user_id,
            'email': data['email']
        }, 201)
    else:
        return ResponseHelper.error_response('Failed to register user', 'REGISTRATION_FAILED', 500)

# Test endpoint for user login
@app.route('/api/v1/auth/login', methods=['POST'])
@require_json
def login_user():
    """
    Login user
    
    Test with curl:
    curl -X POST http://localhost:5000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"john@example.com","password":"password123"}'
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password']
    missing_fields = ValidationHelper.validate_required_fields(data, required_fields)
    
    if missing_fields:
        return ResponseHelper.error_response(f'Missing required fields: {", ".join(missing_fields)}', 'MISSING_FIELDS')
    
    # Authenticate user
    hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
    user = DatabaseManager.execute_query(
        "SELECT user_id, full_name, email FROM users WHERE email = %s AND password = %s",
        (data['email'], hashed_password),
        fetch_one=True
    )
    
    if user:
        session['user_id'] = user['user_id']
        session['full_name'] = user['full_name']
        return ResponseHelper.success_response('Login successful', {
            'user_id': user['user_id'],
            'full_name': user['full_name'],
            'email': user['email']
        })
    else:
        return ResponseHelper.error_response('Invalid email or password', 'INVALID_CREDENTIALS', 401)

# Test endpoint for user logout
@app.route('/api/v1/auth/logout', methods=['POST'])
@require_auth
def logout_user():
    """
    Logout user
    
    Test with curl:
    curl -X POST http://localhost:5000/api/v1/auth/logout
    """
    session.clear()
    return ResponseHelper.success_response('Logout successful')

# Test endpoint for getting all movies
@app.route('/api/v1/movies', methods=['GET'])
def get_movies():
    """
    Get all movies with pagination
    
    Test with curl:
    curl -X GET "http://localhost:5000/api/v1/movies?page=1&limit=10"
    """
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    offset = (page - 1) * limit
    
    movies = DatabaseManager.execute_query(
        "SELECT * FROM movies LIMIT %s OFFSET %s",
        (limit, offset),
        fetch_all=True
    )
    
    # Get total count for pagination
    total_count = DatabaseManager.execute_query(
        "SELECT COUNT(*) as count FROM movies",
        fetch_one=True
    )
    
    if movies is not None:
        return ResponseHelper.success_response('Movies retrieved successfully', {
            'movies': movies,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count['count'] if total_count else 0,
                'total_pages': (total_count['count'] + limit - 1) // limit if total_count else 0
            }
        })
    else:
        return ResponseHelper.error_response('Failed to retrieve movies', 'FETCH_FAILED', 500)

# Test endpoint for creating a movie
@app.route('/api/v1/movies', methods=['POST'])
@require_auth
def create_movie():
    """
    Create a new movie
    
    Test with curl (multipart form data):
    curl -X POST http://localhost:5000/api/v1/movies \
    -F 'data={"title":"Test Movie","description":"A test movie","runtime":120,"release_date":"2023-01-01","genres":"Action","cast":"Actor 1","director":"Director 1","producer":"Producer 1","keywords":"test","video_link":"http://example.com"}' \
    -F 'image=@/path/to/image.jpg' e.g @C:/Users/me/Desktop/movies_database/static/images/first.png
    """
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
        image_file = None
    else:
        # Handle multipart form data
        data_json = request.form.get('data')
        data = json.loads(data_json) if data_json else {}
        image_file = request.files.get('image')
    
    # Add user_id from session
    data['user_id'] = session['user_id']
    data['catalog_id'] = data.get('catalog_id', str(uuid.uuid4()))
    
    # Validate required fields
    required_fields = ['title', 'description', 'runtime', 'release_date']
    missing_fields = ValidationHelper.validate_required_fields(data, required_fields)
    
    if missing_fields:
        return ResponseHelper.error_response(f'Missing required fields: {", ".join(missing_fields)}', 'MISSING_FIELDS')
    
    # Handle image upload
    image_filename = None
    if image_file:
        image_filename = FileHelper.save_uploaded_file(image_file, app.config['UPLOAD_FOLDER'])
    
    # Insert movie into database
    result = DatabaseManager.execute_query("""
        INSERT INTO movies (
            user_id, catalog_id, title, description, runtime, release_date, genres, 
            cast, director, producer, keywords, images, video_link
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data['user_id'], data['catalog_id'], data['title'], data['description'],
        data['runtime'], data['release_date'], data.get('genres', ''),
        data.get('cast', ''), data.get('director', ''), data.get('producer', ''),
        data.get('keywords', ''), image_filename, data.get('video_link', '')
    ))
    
    if result:
        return ResponseHelper.success_response('Movie created successfully', {
            'catalog_id': data['catalog_id'],
            'title': data['title']
        }, 201)
    else:
        return ResponseHelper.error_response('Failed to create movie', 'CREATE_FAILED', 500)

# Test endpoint for getting a specific movie
@app.route('/api/v1/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """
    Get a specific movie by ID
    
    Test with curl:
    curl -X GET http://localhost:5000/api/v1/movies/1
    """
    movie = DatabaseManager.execute_query(
        "SELECT * FROM movies WHERE movie_id = %s",
        (movie_id,),
        fetch_one=True
    )
    
    if movie:
        return ResponseHelper.success_response('Movie retrieved successfully', {'movie': movie})
    else:
        return ResponseHelper.error_response('Movie not found', 'MOVIE_NOT_FOUND', 404)

# Test endpoint for updating a movie
@app.route('/api/v1/movies/<int:movie_id>', methods=['PUT'])
@require_auth
@require_json
def update_movie(movie_id):
    """
    Update a specific movie
    
    Test with curl:
    curl -X PUT http://localhost:5000/api/v1/movies/1 \
    -H "Content-Type: application/json" \
    -d '{"title":"Updated Movie","description":"Updated description","runtime":150}'
    """
    data = request.get_json()
    
    # Check if movie exists and belongs to user
    existing_movie = DatabaseManager.execute_query(
        "SELECT user_id FROM movies WHERE movie_id = %s",
        (movie_id,),
        fetch_one=True
    )
    
    if not existing_movie:
        return ResponseHelper.error_response('Movie not found', 'MOVIE_NOT_FOUND', 404)
    
    if existing_movie['user_id'] != session['user_id']:
        return ResponseHelper.error_response('Access denied', 'ACCESS_DENIED', 403)
    
    # Build update query dynamically
    update_fields = []
    update_values = []
    
    allowed_fields = ['title', 'description', 'runtime', 'release_date', 'genres', 'cast', 'director', 'producer', 'keywords', 'video_link']
    
    for field in allowed_fields:
        if field in data:
            update_fields.append(f"{field} = %s")
            update_values.append(data[field])
    
    if not update_fields:
        return ResponseHelper.error_response('No valid fields to update', 'NO_UPDATE_FIELDS')
    
    update_values.append(movie_id)
    query = f"UPDATE movies SET {', '.join(update_fields)} WHERE movie_id = %s"
    
    result = DatabaseManager.execute_query(query, update_values)
    
    if result:
        return ResponseHelper.success_response('Movie updated successfully')
    else:
        return ResponseHelper.error_response('Failed to update movie', 'UPDATE_FAILED', 500)

# Test endpoint for deleting a movie
@app.route('/api/v1/movies/<int:movie_id>', methods=['DELETE'])
@require_auth
def delete_movie(movie_id):
    """
    Delete a specific movie
    
    Test with curl:
    curl -X DELETE http://localhost:5000/api/v1/movies/1
    """
    # Check if movie exists and belongs to user
    existing_movie = DatabaseManager.execute_query(
        "SELECT user_id FROM movies WHERE movie_id = %s",
        (movie_id,),
        fetch_one=True
    )
    
    if not existing_movie:
        return ResponseHelper.error_response('Movie not found', 'MOVIE_NOT_FOUND', 404)
    
    if existing_movie['user_id'] != session['user_id']:
        return ResponseHelper.error_response('Access denied', 'ACCESS_DENIED', 403)
    
    result = DatabaseManager.execute_query(
        "DELETE FROM movies WHERE movie_id = %s",
        (movie_id,)
    )
    
    if result:
        return ResponseHelper.success_response('Movie deleted successfully')
    else:
        return ResponseHelper.error_response('Failed to delete movie', 'DELETE_FAILED', 500)

# Test endpoint for getting user's dashboard data
@app.route('/api/v1/dashboard', methods=['GET'])
@require_auth
def get_dashboard():
    """
    Get dashboard data for authenticated user
    
    Test with curl:
    curl -X GET http://localhost:5000/api/v1/dashboard
    """
    user_id = session['user_id']
    
    movies = DatabaseManager.execute_query(
        "SELECT movie_id, title, runtime, genres, cast, director, producer, release_date, images FROM movies WHERE user_id = %s",
        (user_id,),
        fetch_all=True
    )
    
    movie_count = DatabaseManager.execute_query(
        "SELECT COUNT(*) as count FROM movies WHERE user_id = %s",
        (user_id,),
        fetch_one=True
    )
    
    if movies is not None:
        return ResponseHelper.success_response('Dashboard data retrieved successfully', {
            'movies': movies,
            'total_movies': movie_count['count'] if movie_count else 0,
            'user_id': user_id
        })
    else:
        return ResponseHelper.error_response('Failed to retrieve dashboard data', 'FETCH_FAILED', 500)

# ===========
# SERVER-RENDERED ROUTES
# ===========

class AuthService:
    """Reusable authentication service"""
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user and return user data"""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return DatabaseManager.execute_query(
            "SELECT user_id, full_name, email FROM users WHERE email = %s AND password = %s",
            (email, hashed_password),
            fetch_one=True
        )
    
    @staticmethod
    def register_user(user_data):
        """Register new user"""
        # Validate required fields
        required_fields = ['full_name', 'email', 'password', 'phone']
        missing_fields = ValidationHelper.validate_required_fields(user_data, required_fields)
        
        if missing_fields:
            return {'success': False, 'message': f'Missing required fields: {", ".join(missing_fields)}'}
        
        # Validate email format
        if not ValidationHelper.validate_email(user_data['email']):
            return {'success': False, 'message': 'Invalid email format'}
        
        # Check if user already exists
        existing_user = DatabaseManager.execute_query(
            "SELECT email FROM users WHERE email = %s",
            (user_data['email'],),
            fetch_one=True
        )
        
        if existing_user:
            return {'success': False, 'message': 'User with this email already exists'}
        
        # Create new user
        user_id = uuid.uuid4().int
        hashed_password = hashlib.sha256(user_data['password'].encode()).hexdigest()
        
        result = DatabaseManager.execute_query(
            "INSERT INTO users (user_id, full_name, email, password, phone) VALUES (%s, %s, %s, %s, %s)",
            (user_id, user_data['full_name'], user_data['email'], hashed_password, user_data['phone'])
        )
        
        if result:
            return {'success': True, 'message': 'Registration successful! Please sign in.', 'user_id': user_id}
        else:
            return {'success': False, 'message': 'Registration failed. Please try again.'}

class MovieService:
    """Reusable movie service"""
    
    @staticmethod
    def get_movies(user_id=None, limit=None, offset=None):
        """Get movies with optional filtering and pagination"""
        if user_id:
            query = "SELECT * FROM movies WHERE user_id = %s"
            params = [user_id]
        else:
            query = "SELECT * FROM movies"
            params = []
        
        if limit:
            query += " LIMIT %s"
            params.append(limit)
            
        if offset:
            query += " OFFSET %s"
            params.append(offset)
        
        return DatabaseManager.execute_query(query, params, fetch_all=True)
    
    @staticmethod
    def get_movie_by_id(movie_id):
        """Get a specific movie by ID"""
        return DatabaseManager.execute_query(
            "SELECT * FROM movies WHERE movie_id = %s",
            (movie_id,),
            fetch_one=True
        )
    
    @staticmethod
    def create_movie(movie_data, user_id):
        """Create a new movie"""
        # Validate required fields
        required_fields = ['title', 'description', 'runtime', 'release_date']
        missing_fields = ValidationHelper.validate_required_fields(movie_data, required_fields)
        
        if missing_fields:
            return {'success': False, 'message': f'Missing required fields: {", ".join(missing_fields)}'}
        
        # Add user_id and catalog_id
        movie_data['user_id'] = user_id
        movie_data['catalog_id'] = movie_data.get('catalog_id', str(uuid.uuid4()))
        
        # Handle image upload if present
        image_filename = None
        if 'image' in request.files:
            image_file = request.files['image']
            image_filename = FileHelper.save_uploaded_file(image_file, app.config['UPLOAD_FOLDER'])
        
        result = DatabaseManager.execute_query("""
            INSERT INTO movies (
                user_id, catalog_id, title, description, runtime, release_date, genres, 
                cast, director, producer, keywords, images, video_link
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            movie_data['user_id'], movie_data['catalog_id'], movie_data['title'], 
            movie_data['description'], movie_data['runtime'], movie_data['release_date'], 
            movie_data.get('genres', ''), movie_data.get('cast', ''), 
            movie_data.get('director', ''), movie_data.get('producer', ''),
            movie_data.get('keywords', ''), image_filename, movie_data.get('video_link', '')
        ))
        
        if result:
            return {'success': True, 'message': 'Movie added successfully!'}
        else:
            return {'success': False, 'message': 'Failed to create movie'}
    
    @staticmethod
    def update_movie(movie_id, movie_data, user_id):
        """Update an existing movie"""
        # Check if movie exists and belongs to user
        existing_movie = DatabaseManager.execute_query(
            "SELECT user_id FROM movies WHERE movie_id = %s",
            (movie_id,),
            fetch_one=True
        )
        
        if not existing_movie:
            return {'success': False, 'message': 'Movie not found'}
        
        if existing_movie['user_id'] != user_id:
            return {'success': False, 'message': 'Access denied'}
        
        # Handle image upload if present
        image_filename = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                image_filename = FileHelper.save_uploaded_file(image_file, app.config['UPLOAD_FOLDER'])
        
        # Build update query dynamically
        update_fields = []
        update_values = []
        
        allowed_fields = ['title', 'description', 'runtime', 'release_date', 'genres', 'cast', 'director', 'producer', 'keywords', 'video_link']
        
        for field in allowed_fields:
            if field in movie_data and movie_data[field]:
                update_fields.append(f"{field} = %s")
                update_values.append(movie_data[field])
        
        if image_filename:
            update_fields.append("images = %s")
            update_values.append(image_filename)
        
        if not update_fields:
            return {'success': False, 'message': 'No valid fields to update'}
        
        update_values.append(movie_id)
        query = f"UPDATE movies SET {', '.join(update_fields)} WHERE movie_id = %s"
        
        result = DatabaseManager.execute_query(query, update_values)
        
        if result:
            return {'success': True, 'message': 'Movie updated successfully!'}
        else:
            return {'success': False, 'message': 'Failed to update movie'}
    
    @staticmethod
    def delete_movie(movie_id, user_id):
        """Delete a movie"""
        # Check if movie exists and belongs to user
        existing_movie = DatabaseManager.execute_query(
            "SELECT user_id FROM movies WHERE movie_id = %s",
            (movie_id,),
            fetch_one=True
        )
        
        if not existing_movie:
            return {'success': False, 'message': 'Movie not found'}
        
        if existing_movie['user_id'] != user_id:
            return {'success': False, 'message': 'Access denied'}
        
        result = DatabaseManager.execute_query(
            "DELETE FROM movies WHERE movie_id = %s",
            (movie_id,)
        )
        
        if result:
            return {'success': True, 'message': 'Movie deleted successfully!'}
        else:
            return {'success': False, 'message': 'Failed to delete movie'}

# =========
# SERVER-RENDERED ROUTES
# =========

@app.route('/')
def home():
    """
    Home page - displays all movies
    Test by visiting: http://localhost:5000/
    """
    page = int(request.args.get('page', 1))
    limit = 12  # Display 12 movies per page
    offset = (page - 1) * limit
    
    movies = MovieService.get_movies(limit=limit, offset=offset)
    
    # Get total count for pagination
    total_count = DatabaseManager.execute_query(
        "SELECT COUNT(*) as count FROM movies",
        fetch_one=True
    )
    
    total_pages = (total_count['count'] + limit - 1) // limit if total_count else 0
    
    return render_template('index.html', 
                         movies=movies or [], 
                         page=page, 
                         total_pages=total_pages,
                         has_prev=page > 1,
                         has_next=page < total_pages)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    User registration page
    Test by visiting: http://localhost:5000/signup
    """
    if request.method == 'GET':
        return render_template('signup.html')
    
    # Handle POST request using reusable service
    user_data = {
        'full_name': request.form.get('full_name'),
        'email': request.form.get('email'),
        'password': request.form.get('password'),
        'confirm_password': request.form.get('confirm_password'),
        'phone': request.form.get('phone')
    }
    
    # Validate password confirmation
    if user_data['password'] != user_data['confirm_password']:
        flash('Passwords do not match!', 'error')
        return redirect(url_for('signup'))
    
    result = AuthService.register_user(user_data)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('signup'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login page
    Test by visiting: http://localhost:5000/login
    """
    if request.method == 'GET':
        return render_template('signin.html')
    
    # Handle POST request using reusable service
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        flash('Both email and password are required!', 'error')
        return redirect(url_for('login'))
    
    user = AuthService.authenticate_user(email, password)
    
    if user:
        session['user_id'] = user['user_id']
        session['full_name'] = user['full_name']
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid email or password.', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """
    User logout
    Test by visiting: http://localhost:5000/logout
    """
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    """
    User dashboard - displays user's movies
    Test by visiting: http://localhost:5000/dashboard (requires login)
    """
    if 'user_id' not in session:
        flash('Please log in to access your dashboard.', 'error')
        return redirect(url_for('login'))
    
    movies = MovieService.get_movies(user_id=session['user_id'])
    
    return render_template('dashboard.html', 
                         movies=movies or [], 
                         user_id=session['user_id'],
                         full_name=session.get('full_name'))

@app.route('/details/<int:movie_id>')
def movie_details(movie_id):
    """
    Movie details page
    Test by visiting: http://localhost:5000/details/1
    """
    movie = MovieService.get_movie_by_id(movie_id)
    
    if not movie:
        flash("Movie not found", "error")
        return redirect(url_for('home'))
    
    # Check if current user owns this movie
    is_owner = 'user_id' in session and session['user_id'] == movie.get('user_id')
    
    return render_template('details.html', 
                         movie=movie, 
                         is_owner=is_owner)

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    """
    Add movie page
    Test by visiting: http://localhost:5000/add_movie (requires login)
    """
    if 'user_id' not in session:
        flash('Please log in to add a movie.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        return render_template('add_movie.html')
    
    # Handle POST request using reusable service
    movie_data = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'runtime': request.form.get('runtime'),
        'release_date': request.form.get('release_date'),
        'genres': request.form.get('genres'),
        'cast': request.form.get('cast'),
        'director': request.form.get('director'),
        'producer': request.form.get('producer'),
        'keywords': request.form.get('keywords'),
        'video_link': request.form.get('video_link'),
        'catalog_id': request.form.get('catalog_id')
    }
    
    result = MovieService.create_movie(movie_data, session['user_id'])
    
    if result['success']:
        flash(result['message'], 'success')
        return redirect(url_for('dashboard'))
    else:
        flash(result['message'], 'error')
        return render_template('add_movie.html', movie_data=movie_data)

@app.route('/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie_page(movie_id):
    """
    Edit movie page
    Test by visiting: http://localhost:5000/edit/1 (requires login and ownership)
    """
    if 'user_id' not in session:
        flash('Please log in to edit movies.', 'error')
        return redirect(url_for('login'))
    
    movie = MovieService.get_movie_by_id(movie_id)
    
    if not movie:
        flash('Movie not found', 'error')
        return redirect(url_for('dashboard'))
    
    if movie['user_id'] != session['user_id']:
        flash('Access denied. You can only edit your own movies.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'GET':
        return render_template('edit_movie.html', movie=movie)
    
    # Handle POST request using reusable service
    movie_data = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'runtime': request.form.get('runtime'),
        'release_date': request.form.get('release_date'),
        'genres': request.form.get('genres'),
        'cast': request.form.get('cast'),
        'director': request.form.get('director'),
        'producer': request.form.get('producer'),
        'keywords': request.form.get('keywords'),
        'video_link': request.form.get('video_link')
    }
    
    result = MovieService.update_movie(movie_id, movie_data, session['user_id'])
    
    if result['success']:
        flash(result['message'], 'success')
        return redirect(url_for('movie_details', movie_id=movie_id))
    else:
        flash(result['message'], 'error')
        return render_template('edit_movie.html', movie=movie)

@app.route('/delete/<int:movie_id>', methods=['POST'])
def delete_movie_page(movie_id):
    """
    Delete movie (POST only for security)
    Test with a form that posts to: http://localhost:5000/delete/1
    """
    if 'user_id' not in session:
        flash('Please log in to delete movies.', 'error')
        return redirect(url_for('login'))
    
    result = MovieService.delete_movie(movie_id, session['user_id'])
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('dashboard'))

# =========
# ERROR HANDLERS
# =========

@app.errorhandler(404)
def not_found(error):
    return ResponseHelper.error_response('Endpoint not found', 'NOT_FOUND', 404)

@app.errorhandler(405)
def method_not_allowed(error):
    return ResponseHelper.error_response('Method not allowed', 'METHOD_NOT_ALLOWED', 405)

@app.errorhandler(500)
def internal_error(error):
    return ResponseHelper.error_response('Internal server error', 'INTERNAL_ERROR', 500)

# =========
# MAIN APPLICATION
# =========

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)