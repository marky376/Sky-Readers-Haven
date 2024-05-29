from flask import Blueprint, request, jsonify

main = Blueprint('main', __name__)

@main.route('/search', methods=['GET'])
def search():
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
def get_books():
    from .models import Book  # Import here to avoid circular import
    books = Book.query.all()
    books_list = [{'title': book.title, 'author': book.author.name} for book in books]
    return jsonify(books_list)
