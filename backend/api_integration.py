import requests
from flask import current_app

def search_books(query):
    """Search for books using Google Books API"""
    # Get API key from Flask config
    api_key = current_app.config.get('GOOGLE_BOOKS_API_KEY')
    
    # Construct the URL for the Google Books API search endpoint
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}'

    # Send a GET request to the API endpoint
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the response as JSON
        books = response.json()

        # Return the list of book items from the response
        return books.get('items', [])

    # If the request was not successful, return None
    return None


def get_book_by_id(volume_id):
    """Fetch a single book volume by its Google Books volume id."""
    api_key = current_app.config.get('GOOGLE_BOOKS_API_KEY')
    url = f'https://www.googleapis.com/books/v1/volumes/{volume_id}?key={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None