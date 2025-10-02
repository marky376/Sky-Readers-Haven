from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Import db from app module to avoid circular imports
from .app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    reviews = db.relationship('Review', backref='user', lazy=True)
    cart = db.relationship('Cart', backref='user', uselist=False, lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    books = db.relationship('Book', backref='author', lazy=True)

    def __repr__(self):
        return f'<Author {self.name}>'

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    books = db.relationship('Book', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    published_date = db.Column(db.Date, nullable=True)
    isbn = db.Column(db.String(13), unique=True, nullable=True)
    price = db.Column(db.Float, default=9.99, nullable=False)  # Default book price
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    reviews = db.relationship('Review', backref='book', lazy=True)

    def __repr__(self):
        return f'<Book {self.title}>'

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=True)  # Review title
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    verified_purchase = db.Column(db.Boolean, default=False, nullable=False)  # Did user buy the book?
    helpful_count = db.Column(db.Integer, default=0, nullable=False)  # Helpful votes
    unhelpful_count = db.Column(db.Integer, default=0, nullable=False)  # Not helpful votes
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    votes = db.relationship('ReviewVote', backref='review', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Review {self.content[:20]}>'


class ReviewVote(db.Model):
    __tablename__ = 'review_votes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    is_helpful = db.Column(db.Boolean, nullable=False)  # True = helpful, False = not helpful
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Ensure user can only vote once per review
    __table_args__ = (db.UniqueConstraint('user_id', 'review_id', name='unique_user_review_vote'),)

    def __repr__(self):
        return f'<ReviewVote user={self.user_id} review={self.review_id}>'

class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new', nullable=False)  # new, read, replied
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<ContactMessage from {self.email}>'

class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    def get_total_price(self):
        """Calculate total price of all items in cart"""
        return sum(item.get_subtotal() for item in self.items)

    def get_total_items(self):
        """Get total number of items (sum of quantities)"""
        return sum(item.quantity for item in self.items)

    def __repr__(self):
        return f'<Cart for User {self.user_id}>'

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price at time of adding to cart
    added_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    book = db.relationship('Book', backref='cart_items', lazy=True)

    def get_subtotal(self):
        """Calculate subtotal for this cart item"""
        return self.price * self.quantity

    def __repr__(self):
        return f'<CartItem Book {self.book_id} x {self.quantity}>'

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    
    # Order status: pending, processing, shipped, delivered, cancelled
    status = db.Column(db.String(20), default='pending', nullable=False)
    
    # Pricing
    subtotal = db.Column(db.Float, nullable=False)
    tax = db.Column(db.Float, nullable=False)
    shipping_cost = db.Column(db.Float, default=0.0, nullable=False)
    total = db.Column(db.Float, nullable=False)
    
    # Shipping information
    shipping_name = db.Column(db.String(120), nullable=False)
    shipping_email = db.Column(db.String(120), nullable=False)
    shipping_phone = db.Column(db.String(20), nullable=True)
    shipping_address = db.Column(db.String(255), nullable=False)
    shipping_city = db.Column(db.String(100), nullable=False)
    shipping_state = db.Column(db.String(100), nullable=True)
    shipping_zip = db.Column(db.String(20), nullable=False)
    shipping_country = db.Column(db.String(100), nullable=False)
    
    # Payment information
    payment_method = db.Column(db.String(50), nullable=False)  # card, paypal, etc.
    payment_status = db.Column(db.String(20), default='pending', nullable=False)  # pending, paid, failed
    transaction_id = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    user = db.relationship('User', backref='orders', lazy=True)
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price at time of order
    
    # Relationships
    book = db.relationship('Book', backref='order_items', lazy=True)
    
    def get_subtotal(self):
        """Calculate subtotal for this order item"""
        return self.price * self.quantity
    
    def __repr__(self):
        return f'<OrderItem Order {self.order_id} Book {self.book_id}>'


class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    notes = db.Column(db.String(500))  # Optional personal notes
    
    # Relationships
    user = db.relationship('User', backref='wishlist_items', lazy=True)
    book = db.relationship('Book', backref='wishlist_items', lazy=True)
    
    # Ensure user can only add same book once
    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='unique_user_book_wishlist'),)
    
    def __repr__(self):
        return f'<Wishlist User {self.user_id} Book {self.book_id}>'
