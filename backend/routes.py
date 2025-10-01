from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_jwt_extended import create_access_token, jwt_required
from .app import db
from .models import User, Book
from werkzeug.security import generate_password_hash, check_password_hash
from .api_integration import search_books

main = Blueprint('main', __name__)

# Web Routes (Template-based)
@main.route('/')
def home():
    """Home page route"""
    return render_template('index.html')

@main.route('/about')
def about():
    """About page route"""
    return render_template('about.html')

@main.route('/books')
def books():
    """Books catalog page route"""
    return render_template('books.html')

@main.route('/contact')
def contact():
    """Contact page route"""
    return render_template('contact.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Login page route"""
    if request.method == 'GET':
        return render_template('login.html')
    
    # Handle POST request for login
    data = request.get_json() if request.is_json else request.form
    username = data.get('username')
    password = data.get('password')
    # allow login by username or email
    user = User.query.filter((User.username==username)|(User.email==username)).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.username)
        session['username'] = user.username
        if request.is_json:
            return jsonify({'access_token': access_token}), 200
        else:
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))

    if request.is_json:
        return jsonify({'message': 'Invalid credentials'}), 401
    else:
        flash('Invalid username or password', 'error')
        return render_template('login.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page route"""
    if request.method == 'GET':
        return render_template('signup.html')
    
    # Handle POST request for registration
    data = request.get_json() if request.is_json else request.form
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm = data.get('confirm_password') or data.get('confirm')

    if not username or not email or not password:
        flash('Please fill all required fields', 'error')
        return render_template('signup.html')

    if password != confirm:
        flash('Passwords do not match', 'error')
        return render_template('signup.html')

    if User.query.filter((User.username==username)|(User.email==email)).first():
        flash('User with that username or email already exists', 'error')
        return render_template('signup.html')

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    flash('Registration successful! Please log in.', 'success')
    return redirect(url_for('main.login'))

# API Routes (JSON-based)
@main.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'User already exists'}), 400
    new_user = User(username=data['username'], email=data['email'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@main.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.username)
        return jsonify({'access_token': access_token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@main.route('/search', methods=['GET'])
def search():
    """Search books using Google Books API and render results."""
    query = request.args.get('query')
    if not query:
        # Render books page with no results
        return render_template('books.html', books=[])

    books = search_books(query) or []

    # Convert Google Books items to a simple dict for the template
    results = []
    for item in books:
        v = item.get('volumeInfo', {})
        results.append({
            'id': item.get('id'),
            'title': v.get('title'),
            'authors': v.get('authors'),
            'description': v.get('description'),
            'publishedDate': v.get('publishedDate'),
            'image': (v.get('imageLinks') or {}).get('thumbnail')
        })

    # If the request is expecting JSON (ajax), return JSON
    if request.is_json or request.args.get('format') == 'json':
        return jsonify(results)

    return render_template('books.html', books=results)


@main.route('/book/<volume_id>')
def book_detail(volume_id):
    from .api_integration import get_book_by_id
    item = get_book_by_id(volume_id)
    if not item:
        flash('Book not found', 'error')
        return redirect(url_for('main.books'))
    v = item.get('volumeInfo', {})
    book = {
        'title': v.get('title'),
        'authors': v.get('authors'),
        'description': v.get('description'),
        'publishedDate': v.get('publishedDate'),
        'image': (v.get('imageLinks') or {}).get('thumbnail')
    }
    return render_template('book_detail.html', book=book)

@main.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    books = Book.query.all()
    books_list = [{'title': book.title, 'author': book.author.name} for book in books]
    return jsonify(books_list)
