import datetime
# import mysql.connector  # Commented out MySQL
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import hashlib
from werkzeug.utils import secure_filename
import os
import uuid
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# SQLAlchemy Configuration for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ambrose_movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============   
# DATABASE MODELS
# ============   

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(30), unique=True)
    full_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(30))
    date_id = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationship with movies
    movies = db.relationship('Movie', backref='user', lazy=True)
    
    def to_dict(self):
        """Convert User object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'date_id': self.date_id.isoformat() if self.date_id else None
        }

class Movie(db.Model):
    __tablename__ = 'movies'
    
    movie_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(30), db.ForeignKey('users.user_id'), nullable=False)
    catalog_id = db.Column(db.String(255))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    runtime = db.Column(db.String(255))
    release_date = db.Column(db.String(50))
    genres = db.Column(db.String(255))
    cast = db.Column(db.String(255))
    director = db.Column(db.String(255))
    producer = db.Column(db.String(255))
    keywords = db.Column(db.String(255))
    images = db.Column(db.String(255))
    video_link = db.Column(db.Text)
    date_id = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        """Convert Movie object to dictionary"""
        return {
            'movie_id': self.movie_id,
            'user_id': self.user_id,
            'catalog_id': self.catalog_id,
            'title': self.title,
            'description': self.description,
            'runtime': self.runtime,
            'release_date': self.release_date,
            'genres': self.genres,
            'cast': self.cast,
            'director': self.director,
            'producer': self.producer,
            'keywords': self.keywords,
            'images': self.images,
            'video_link': self.video_link,
            'date_id': self.date_id.isoformat() if self.date_id else None
        }

class Actor(db.Model):
    __tablename__ = 'actors'
    
    actor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    birthdate = db.Column(db.Date)
    gender = db.Column(db.String(10))
    nationality = db.Column(db.String(255))
    date_id = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Director(db.Model):
    __tablename__ = 'directors'
    
    director_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    birthdate = db.Column(db.Date)
    nationality = db.Column(db.String(255))
    date_id = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Genre(db.Model):
    __tablename__ = 'genres'
    
    genre_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    date_id = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Catalog(db.Model):
    __tablename__ = 'catalog'
    
    id = db.Column(db.Integer, primary_key=True)
    catalog_id = db.Column(db.String(30))
    name = db.Column(db.String(255))
    date_id = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# ============   
# REUSABLE COMPONENTS (Updated for SQLAlchemy)
# ============   

class DatabaseManager:
    """Reusable database manager using SQLAlchemy"""
    
    @staticmethod
    def execute_query(query, params=None, fetch_one=False, fetch_all=False):
        """Execute raw SQL query with SQLAlchemy"""
        try:
            if params:
                result = db.session.execute(text(query), params)
            else:
                result = db.session.execute(text(query))
            
            if fetch_one:
                row = result.fetchone()
                return row._asdict() if row else None
            elif fetch_all:
                rows = result.fetchall()
                return [row._asdict() for row in rows] if rows else []
            else:
                db.session.commit()
                return result.rowcount
                
        except Exception as err:
            print(f"Query execution error: {err}")
            db.session.rollback()
            return None

    @staticmethod
    def create_user(user_data):
        """Create a new user using SQLAlchemy ORM"""
        try:
            user = User(
                user_id=user_data.get('user_id'),
                full_name=user_data.get('full_name'),
                email=user_data.get('email'),
                password=user_data.get('password'),
                phone=user_data.get('phone')
            )
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as err:
            print(f"User creation error: {err}")
            db.session.rollback()
            return None

    @staticmethod
    def get_user_by_email(email):
        """Get user by email using SQLAlchemy ORM"""
        try:
            return User.query.filter_by(email=email).first()
        except Exception as err:
            print(f"User query error: {err}")
            return None

    @staticmethod
    def create_movie(movie_data):
        """Create a new movie using SQLAlchemy ORM"""
        try:
            movie = Movie(
                user_id=movie_data.get('user_id'),
                catalog_id=movie_data.get('catalog_id'),
                title=movie_data.get('title'),
                description=movie_data.get('description'),
                runtime=movie_data.get('runtime'),
                release_date=movie_data.get('release_date'),
                genres=movie_data.get('genres'),
                cast=movie_data.get('cast'),
                director=movie_data.get('director'),
                producer=movie_data.get('producer'),
                keywords=movie_data.get('keywords'),
                images=movie_data.get('images'),
                video_link=movie_data.get('video_link')
            )
            db.session.add(movie)
            db.session.commit()
            return movie
        except Exception as err:
            print(f"Movie creation error: {err}")
            db.session.rollback()
            return None

    @staticmethod
    def get_movies(user_id=None, limit=None, offset=None):
        """Get movies using SQLAlchemy ORM - FIXED VERSION"""
        try:
            query = Movie.query
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            if offset:
                query = query.offset(offset)
            
            if limit:
                query = query.limit(limit)
            
            movies = query.all()
            # Use the to_dict() method to properly convert to dictionaries
            return [movie.to_dict() for movie in movies]
        except Exception as err:
            print(f"Movies query error: {err}")
            return []

    @staticmethod
    def get_movie_by_id(movie_id):
        """Get movie by ID using SQLAlchemy ORM - FIXED VERSION"""
        try:
            movie = Movie.query.get(movie_id)
            if movie:
                return movie.to_dict()
            return None
        except Exception as err:
            print(f"Movie query error: {err}")
            return None

    @staticmethod
    def update_movie(movie_id, movie_data):
        """Update movie using SQLAlchemy ORM"""
        try:
            movie = Movie.query.get(movie_id)
            if not movie:
                return None
            
            for key, value in movie_data.items():
                if hasattr(movie, key) and value is not None:
                    setattr(movie, key, value)
            
            db.session.commit()
            return movie
        except Exception as err:
            print(f"Movie update error: {err}")
            db.session.rollback()
            return None

    @staticmethod
    def delete_movie(movie_id):
        """Delete movie using SQLAlchemy ORM"""
        try:
            movie = Movie.query.get(movie_id)
            if not movie:
                return False
            
            db.session.delete(movie)
            db.session.commit()
            return True
        except Exception as err:
            print(f"Movie deletion error: {err}")
            db.session.rollback()
            return False

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
    existing_user = DatabaseManager.get_user_by_email(data['email'])
    
    if existing_user:
        return ResponseHelper.error_response('User with this email already exists', 'USER_EXISTS', 409)
    
    # Create new user
    user_id = str(uuid.uuid4().int)
    hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
    
    user_data = {
        'user_id': user_id,
        'full_name': data['full_name'],
        'email': data['email'],
        'password': hashed_password,
        'phone': data['phone']
    }
    
    result = DatabaseManager.create_user(user_data)
    
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
    -d '{"email":"udohunyime0@gmail.com","password":"hello"}'
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password']
    missing_fields = ValidationHelper.validate_required_fields(data, required_fields)
    
    if missing_fields:
        return ResponseHelper.error_response(f'Missing required fields: {", ".join(missing_fields)}', 'MISSING_FIELDS')
    
    # Authenticate user
    hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
    user = User.query.filter_by(email=data['email'], password=hashed_password).first()
    
    if user:
        session['user_id'] = user.user_id
        session['full_name'] = user.full_name
        return ResponseHelper.success_response('Login successful', {
            'user_id': user.user_id,
            'full_name': user.full_name,
            'email': user.email
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

# Test endpoint for getting all movies - FIXED VERSION
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
    
    movies = DatabaseManager.get_movies(limit=limit, offset=offset)
    
    # Get total count for pagination
    total_count = Movie.query.count()
    
    if movies is not None:
        return ResponseHelper.success_response('Movies retrieved successfully', {
            'movies': movies,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'total_pages': (total_count + limit - 1) // limit if total_count else 0
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
    
    Test with curl (JSON):
    curl -X POST http://localhost:5000/api/v1/movies \
    -H "Content-Type: application/json" \
    -d '{"title":"Test Movie","description":"A test movie","runtime":"120","release_date":"2023-01-01","genres":"Action","cast":"Actor 1","director":"Director 1","producer":"Producer 1","keywords":"test","video_link":"http://example.com"}'
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
    
    # Prepare movie data
    movie_data = {
        'user_id': data['user_id'],
        'catalog_id': data['catalog_id'],
        'title': data['title'],
        'description': data['description'],
        'runtime': str(data['runtime']),
        'release_date': data['release_date'],
        'genres': data.get('genres', ''),
        'cast': data.get('cast', ''),
        'director': data.get('director', ''),
        'producer': data.get('producer', ''),
        'keywords': data.get('keywords', ''),
        'images': image_filename,
        'video_link': data.get('video_link', '')
    }
    
    result = DatabaseManager.create_movie(movie_data)
    
    if result:
        return ResponseHelper.success_response('Movie created successfully', {
            'catalog_id': data['catalog_id'],
            'title': data['title'],
            'movie_id': result.movie_id
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
    movie = DatabaseManager.get_movie_by_id(movie_id)
    
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
    -d '{"title":"Updated Movie","description":"Updated description","runtime":"150"}'
    """
    data = request.get_json()
    
    # Check if movie exists and belongs to user
    existing_movie = Movie.query.get(movie_id)
    
    if not existing_movie:
        return ResponseHelper.error_response('Movie not found', 'MOVIE_NOT_FOUND', 404)
    
    if existing_movie.user_id != session['user_id']:
        return ResponseHelper.error_response('Access denied', 'ACCESS_DENIED', 403)
    
    # Filter allowed fields
    allowed_fields = ['title', 'description', 'runtime', 'release_date', 'genres', 'cast', 'director', 'producer', 'keywords', 'video_link']
    update_data = {k: v for k, v in data.items() if k in allowed_fields and v is not None}
    
    if not update_data:
        return ResponseHelper.error_response('No valid fields to update', 'NO_UPDATE_FIELDS')
    
    result = DatabaseManager.update_movie(movie_id, update_data)
    
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
    existing_movie = Movie.query.get(movie_id)
    
    if not existing_movie:
        return ResponseHelper.error_response('Movie not found', 'MOVIE_NOT_FOUND', 404)
    
    if existing_movie.user_id != session['user_id']:
        return ResponseHelper.error_response('Access denied', 'ACCESS_DENIED', 403)
    
    result = DatabaseManager.delete_movie(movie_id)
    
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
    
    movies = DatabaseManager.get_movies(user_id=user_id)
    movie_count = Movie.query.filter_by(user_id=user_id).count()
    
    if movies is not None:
        return ResponseHelper.success_response('Dashboard data retrieved successfully', {
            'movies': movies,
            'total_movies': movie_count,
            'user_id': user_id
        })
    else:
        return ResponseHelper.error_response('Failed to retrieve dashboard data', 'FETCH_FAILED', 500)

# ===========
# SERVER-RENDERED ROUTES (Updated for SQLAlchemy)
# ===========

class AuthService:
    """Reusable authentication service"""
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user and return user data"""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user = User.query.filter_by(email=email, password=hashed_password).first()
        
        if user:
            return {
                'user_id': user.user_id,
                'full_name': user.full_name,
                'email': user.email
            }
        return None
    
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
        existing_user = DatabaseManager.get_user_by_email(user_data['email'])
        
        if existing_user:
            return {'success': False, 'message': 'User with this email already exists'}
        
        # Create new user
        user_id = str(uuid.uuid4().int)
        hashed_password = hashlib.sha256(user_data['password'].encode()).hexdigest()
        
        new_user_data = {
            'user_id': user_id,
            'full_name': user_data['full_name'],
            'email': user_data['email'],
            'password': hashed_password,
            'phone': user_data['phone']
        }
        
        result = DatabaseManager.create_user(new_user_data)
        
        if result:
            return {'success': True, 'message': 'Registration successful! Please sign in.', 'user_id': user_id}
        else:
            return {'success': False, 'message': 'Registration failed. Please try again.'}

class MovieService:
    """Reusable movie service"""
    
    @staticmethod
    def get_movies(user_id=None, limit=None, offset=None):
        """Get movies with optional filtering and pagination"""
        return DatabaseManager.get_movies(user_id=user_id, limit=limit, offset=offset)
    
    @staticmethod
    def get_movie_by_id(movie_id):
        """Get a specific movie by ID"""
        return DatabaseManager.get_movie_by_id(movie_id)
    
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
        
        # Prepare movie data for database
        db_movie_data = {
            'user_id': movie_data['user_id'],
            'catalog_id': movie_data['catalog_id'],
            'title': movie_data['title'],
            'description': movie_data['description'],
            'runtime': str(movie_data['runtime']),
            'release_date': movie_data['release_date'],
            'genres': movie_data.get('genres', ''),
            'cast': movie_data.get('cast', ''),
            'director': movie_data.get('director', ''),
            'producer': movie_data.get('producer', ''),
            'keywords': movie_data.get('keywords', ''),
            'images': image_filename,
            'video_link': movie_data.get('video_link', '')
        }
        
        result = DatabaseManager.create_movie(db_movie_data)
        
        if result:
            return {'success': True, 'message': 'Movie added successfully!'}
        else:
            return {'success': False, 'message': 'Failed to create movie'}
    
    @staticmethod
    def update_movie(movie_id, movie_data, user_id):
        """Update an existing movie"""
        # Check if movie exists and belongs to user
        existing_movie = Movie.query.get(movie_id)
        
        if not existing_movie:
            return {'success': False, 'message': 'Movie not found'}
        
        if existing_movie.user_id != user_id:
            return {'success': False, 'message': 'Access denied'}
        
        # Handle image upload if present
        update_data = {}
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                image_filename = FileHelper.save_uploaded_file(image_file, app.config['UPLOAD_FOLDER'])
                update_data['images'] = image_filename
        
        # Filter allowed fields
        allowed_fields = ['title', 'description', 'runtime', 'release_date', 'genres', 'cast', 'director', 'producer', 'keywords', 'video_link']
        
        for field in allowed_fields:
            if field in movie_data and movie_data[field]:
                update_data[field] = movie_data[field]
        
        if not update_data:
            return {'success': False, 'message': 'No valid fields to update'}
        
        result = DatabaseManager.update_movie(movie_id, update_data)
        
        if result:
            return {'success': True, 'message': 'Movie updated successfully!'}
        else:
            return {'success': False, 'message': 'Failed to update movie'}
    
    @staticmethod
    def delete_movie(movie_id, user_id):
        """Delete a movie"""
        # Check if movie exists and belongs to user
        existing_movie = Movie.query.get(movie_id)
        
        if not existing_movie:
            return {'success': False, 'message': 'Movie not found'}
        
        if existing_movie.user_id != user_id:
            return {'success': False, 'message': 'Access denied'}
        
        result = DatabaseManager.delete_movie(movie_id)
        
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
    total_count = Movie.query.count()
    
    total_pages = (total_count + limit - 1) // limit if total_count else 0
    
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

@app.route('/catalog')
def catalog():
    return render_template('catalog.html')

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
# DATABASE INITIALIZATION
# =========

def init_database():
    """Initialize database tables and sample data"""
    try:
        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Check if data already exists
        if User.query.first():
            print("✓ Sample data already exists!")
            return
        
        print("📊 Inserting sample data...")
        
        # Create sample users
        users_data = [
            {
                'user_id': '1',
                'full_name': 'Unyime Ephraim Udoh',
                'email': 'udohunyime0@gmail.com',
                'password': hashlib.sha256('hello'.encode()).hexdigest(),
                'phone': '09025928492'
            },
            {
                'user_id': '873070981322904351892697539791',
                'full_name': 'Ambrose Ali',
                'email': 'ambrose@gmail.com',
                'password': hashlib.sha256('hello'.encode()).hexdigest(),
                'phone': '08136146684'
            }
        ]
        
        for user_data in users_data:
            user = User(**user_data)
            db.session.add(user)
        
        # Create sample movies
        movies_data = [
            {
                'user_id': '1',
                'catalog_id': '1',
                'title': 'The Dark Knight',
                'description': 'A battle between Batman and Joker',
                'runtime': '152',
                'release_date': '2008-07-18',
                'genres': 'Action, Crime',
                'cast': 'Heath Ledger, Christian Bale, Morgan Freeman',
                'director': 'Christopher Nolan',
                'producer': 'Warner Bros.',
                'keywords': 'Batman, Joker, Gotham',
                'images': 'cover4.jpg',
                'video_link': 'https://www.youtube.com/watch?v=EXeTwQWrcwY'
            },
            {
                'user_id': '1',
                'catalog_id': '2',
                'title': 'Inception',
                'description': 'A thief enters dreams to steal secrets',
                'runtime': '148',
                'release_date': '2010-07-16',
                'genres': 'Sci-Fi, Thriller',
                'cast': 'Leonardo DiCaprio, Joseph Gordon-Levitt, Tom Hardy',
                'director': 'Christopher Nolan',
                'producer': 'Legendary Pictures',
                'keywords': 'Dreams, Heist, Mind',
                'images': 'cover8.jpg',
                'video_link': 'https://www.youtube.com/watch?v=YoHD9XEInc0'
            },
            {
                'user_id': '1',
                'catalog_id': '3',
                'title': 'The Matrix',
                'description': 'A hacker discovers reality is a simulation.',
                'runtime': '136',
                'release_date': '1999-03-31',
                'genres': 'Sci-Fi, Action',
                'cast': 'Keanu Reeves, Laurence Fishburne',
                'director': 'Lana Wachowski, Lilly Wachowski',
                'producer': 'Joel Silver',
                'keywords': 'matrix, simulation, action',
                'images': 'matrix.jpg',
                'video_link': 'https://www.youtube.com/watch?v=vKQi3bBA1y8'
            }
        ]
        
        for movie_data in movies_data:
            movie = Movie(**movie_data)
            db.session.add(movie)
        
        db.session.commit()
        print("✓ Sample data inserted successfully!")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        db.session.rollback()

# Initialize database when app starts
with app.app_context():
    init_database()
    print("="*50)
    print("Flask SQLAlchemy Movie Database Application")
    print("="*50)
    print("Available endpoints:")
    print("  Web Interface:")
    print("    http://localhost:5000/          - Home page")
    print("    http://localhost:5000/signup    - User registration")
    print("    http://localhost:5000/login     - User login")
    print("    http://localhost:5000/dashboard - User dashboard")
    print()
    print("  🔌 API Endpoints:")
    print("    GET  /api/v1/health             - Health check")
    print("    POST /api/v1/auth/register      - Register user")
    print("    POST /api/v1/auth/login         - Login user")
    print("    POST /api/v1/auth/logout        - Logout user")
    print("    GET  /api/v1/movies             - Get movies")
    print("    POST /api/v1/movies             - Create movie")
    print("    GET  /api/v1/movies/<id>        - Get specific movie")
    print("    PUT  /api/v1/movies/<id>        - Update movie")
    print("    DELETE /api/v1/movies/<id>      - Delete movie")
    print("    GET  /api/v1/dashboard          - Get dashboard data")
    print()
    print(" Sample login credentials:")
    print("  Email: udohunyime0@gmail.com")
    print("  Password: hello")
    print("="*50)
    print(" Starting server...")

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