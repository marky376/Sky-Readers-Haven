from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
from .models import db, User, Book
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

@main.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'User already exists'}), 400
    new_user = User(username=data['username'], email=data['email'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.username)
        return jsonify({'access_token': access_token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@main.route('/search', methods=['GET'])
@jwt_required()
def search():
    """
    Search for books based on the provided query parameter.

    Returns:
        If books are found, a JSON response containing the books.
        If no books are found, a JSON response with an error message and status code 404.
        If the query parameter is missing, a JSON response with an error message and status code 400.
    """
    from .api_integration import search_books  # Import here to avoid circular import
    query = request.args.get('query')
    if query:
        books = search_books(query)
        if books:
            return jsonify(books)
        else:
            return jsonify({'error': 'No books found'}), 404
    else:
        return jsonify({'error': 'Query parameter is required'}), 400

@main.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    books = Book.query.all()
    books_list = [{'title': book.title, 'author': book.author.name} for book in books]
    return jsonify(books_list)
