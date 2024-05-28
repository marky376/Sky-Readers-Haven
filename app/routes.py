from flask import Blueprint, request, jsonify
from .api_integration import search_books


main = Blueprint('main', __name__)

@main.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        books = search_books(query)
        if books:
            return jsonify(books)
        else:
            return jsonify({'error': 'No books found'}), 404
    else:
        return jsonify({'error': 'Query parameter is required'}), 400
