// src/App.js

import React, { useState } from 'react';
import BookCard from './components/BookCard';
import SearchBar from './components/SearchBar';
import CartSummary from './components/CartSummary';
import './App.css';

const App = () => {
  const [books, setBooks] = useState([
    { id: 1, title: 'Book 1', author: 'Author 1', price: 10.99, description: 'Description 1' },
    { id: 2, title: 'Book 2', author: 'Author 2', price: 12.99, description: 'Description 2' },
    // Add more books here
  ]);
  const [cart, setCart] = useState([]);

  const handleSearch = (query) => {
    // Implement search logic here
    console.log('Searching for:', query);
  };

  const addToCart = (book) => {
    setCart([...cart, { ...book, quantity: 1 }]);
  };

  return (
    <div className="app">
      <h1>Sky Readers Haven</h1>
      <SearchBar onSearch={handleSearch} />
      <div className="book-list">
        {books.map((book) => (
          <div key={book.id} className="book-item">
            <BookCard {...book} />
            <button onClick={() => addToCart(book)}>Add to Cart</button>
          </div>
        ))}
      </div>
      <CartSummary items={cart} />
    </div>
  );
};

export default App;

