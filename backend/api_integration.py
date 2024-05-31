import requests

API_KEY = 'AIzaSyDHqP9cfL3eoHmDoWNc2X8QLhEH8jK0vBg'

def search_books(query):
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        books = response.json()
        return books['items']
    return None