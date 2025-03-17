# movies_database
A Movie Database
A movie database is a structured collection of information related to movies, including details about the movies themselves (such as title, release year, genre, and ratings), as well as associated data about the people involved in their creation and performance, like directors, actors, and genres. The primary goal of a movie database is to store, organize, and retrieve relevant information in a way that allows users to easily search, browse, and analyze different aspects of the film industry. It can serve various purposes, including cataloging movies, tracking actors' and directors' careers, understanding film trends, or providing movie recommendations. The purpose of this research project was to design and implement a movie database system that enables users to view movies, browse through different genres, and watch movies online, similar to Netflix
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
iii.	Mysql.connector
# Justification of the use of the programming language (Python)
Python has been chosen as the programming language for developing the movie management system and the RESTful API for several compelling reasons. Python comes with a vast ecosystem of libraries and frameworks, which can significantly accelerate the development process. For this project, we will utilize libraries like Flask for web development and MySQL.connector for database management. These libraries have been designed to integrate easily, providing powerful features without requiring a steep learning curve. Python excels at integration with various other technologies, databases, and tools. In this project, Python will integrate seamlessly with
i.	MySQL for data storage and management of movie, actor, and director records.
ii.	XAMPP as a local development environment, providing the Apache web server and MySQL database to run the system locally before deployment.
iii.	Flask enables easy creation of RESTful APIs, which can be consumed by web browsers, mobile apps, or any other client that communicates via HTTP.
Justification for the Use of Flask Framework in the Movie Management System
The Flask framework has been selected for the development of the movie management system and its associated RESTful API for several important reasons. Flask is a micro-framework, meaning it provides only essential tools and features, allowing developers to build applications with minimal overhead. Flask provides excellent support for building RESTful APIs using Flask-RESTful or Flask-RESTX. Flask supports various database technologies, including SQLAlchemy for relational databases (e.g., MySQL, PostgreSQL) and NoSQL databases (e.g., MongoDB).
# Login Page
# API endpoint for login
# Route: Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        phone = request.form['phone']

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
                "INSERT INTO users (full_name, email, password, phone) VALUES (%s, %s, %s, %s)",
                (full_name, email, hashed_password, phone)
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
 
# Registration Page
 
# Dashboard
# API Endpoint to add a movie
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
 
# References
Auber, D., Chiricota, Y., Jourdan, F., & Melanon, G. (2020). Multiscale visualization of small world networks. Proceedings of InfoVis, 75-81.
Ahmed, A., Dwyer, T., Forster, M., Fu, X., Ho, J., Hong, S., Koschützki, D., Murray, C., Nikolov, N., Tarassov, A., Taib, R., & Xu, K. (2021). GEOMI: GEometry for Maximum Insight. Proceedings of Graph Drawing, 468-479.
Batagelj, V. (2022). Analysis of large networks - Islands. Dagstuhl seminar 03361: Algorithmic Aspects of Large and Complex Networks.
Brandes, U., & Erlebach, T. (2021). Network analysis: Methodological foundations. Springer.
Brandes, U., Hoefer, M., & Pich, C. (2020). Affiliation dynamics with an application to movie-actor biographies. Proceedings of EuroVis, 179-186.
Wasserman, S., & Faust, K. (2020). Social Network Analysis: Methods and Applications. Cambridge University Press.
Weible, C. (2021). The Internet Movie Database. Internet Reference Services Quarterly, 6(2), 47-50. https://doi.org/10.1300/J136v06n02_05
