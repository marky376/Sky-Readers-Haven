// src/App.js

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import BookCard from './components/BookCard';
import SearchBar from './components/SearchBar';
import CartSummary from './components/CartSummary';
import AuthForm from './components/AuthForm';
import './App.css';

const App = () => {
  const [books, setBooks] = useState([]);
  const [cart, setCart] = useState([]);
  const [authToken, setAuthToken] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    if (authToken) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
      setIsAuthenticated(true);
    } else {
      delete axios.defaults.headers.common['Authorization'];
      setIsAuthenticated(false);
    }
  }, [authToken]);

  const handleSearch = async (query) => {
    try {
      const response = await axios.get(`/search?query=${query}`);
      setBooks(response.data);
    } catch (error) {
      console.error('Error searching for books:', error);
    }
  };

  const addToCart = (book) => {
    setCart([...cart, { ...book, quantity: 1 }]);
  };

  const handleRegister = async (username, email, password) => {
    try {
      const response = await axios.post('/register', { username, email, password });
      console.log(response.data.message);
    } catch (error) {
      console.error('Error registering user:', error);
    }
  };

  const handleLogin = async (username, password) => {
    try {
      const response = await axios.post('/login', { username, password });
      setAuthToken(response.data.access_token);
    } catch (error) {
      console.error('Error logging in:', error);
    }
  };

  const handleLogout = () => {
    setAuthToken(null);
    setBooks([]);
    setCart([]);
  };

  return (
    <div className="app">
      <h1>Sky Readers Haven</h1>
      {isAuthenticated ? (
        <>
          <button onClick={handleLogout}>Logout</button>
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
        </>
      ) : (
        <AuthForm onRegister={handleRegister} onLogin={handleLogin} />
      )}
    </div>
  );
};

export default App;
