import requests

# API key for accessing the Google Books API
API_KEY = 'AIzaSyDHqP9cfL3eoHmDoWNc2X8QLhEH8jK0vBg'

def search_books(query):
    # Construct the URL for the Google Books API search endpoint
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={API_KEY}'

    # Send a GET request to the API endpoint
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the response as JSON
        books = response.json()

        # Return the list of book items from the response
        return books['items']

    # If the request was not successful, return None
    return None