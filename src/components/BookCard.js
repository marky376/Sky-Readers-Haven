// src/components/BookCard.js

import React from 'react';
import PropTypes from 'prop-types';
import './BookCard.css';

const BookCard = ({ title, author, price, description }) => {
  return (
    <div className="book-card">
      <h3>{title}</h3>
      <p>{author}</p>
      <p>{description}</p>
      <p>${price.toFixed(2)}</p>
    </div>
  );
};

BookCard.propTypes = {
  title: PropTypes.string.isRequired,
  author: PropTypes.string.isRequired,
  price: PropTypes.number.isRequired,
  description: PropTypes.string,
};

export default BookCard;

