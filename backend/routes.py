from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_jwt_extended import create_access_token, jwt_required
from .app import db
from .models import User, Book
from werkzeug.security import generate_password_hash, check_password_hash
from .api_integration import search_books

main = Blueprint('main', __name__)

# Web Routes (Template-based)
@main.route('/')
def home():
    """Home page route"""
    return render_template('index.html')

@main.route('/about')
def about():
    """About page route"""
    return render_template('about.html')

@main.route('/books')
def books():
    """Books catalog page route"""
    return render_template('books.html')

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page route with form submission handler"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validate required fields
        if not all([name, email, subject, message]):
            flash('All fields are required. Please fill out the entire form.', 'error')
            return render_template('contact.html')
        
        # Basic email validation
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            flash('Please enter a valid email address.', 'error')
            return render_template('contact.html')
        
        # Save to database
        try:
            from .models import ContactMessage
            contact_msg = ContactMessage(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            db.session.add(contact_msg)
            db.session.commit()
            
            flash(f'Thank you for contacting us, {name}! We will get back to you soon at {email}.', 'success')
            return redirect(url_for('main.contact'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while sending your message. Please try again later.', 'error')
            return render_template('contact.html')
    
    # GET request - show form
    return render_template('contact.html')

@main.route('/dashboard')
def dashboard():
    """User dashboard - shows after login"""
    if 'username' not in session:
        flash('Please log in to access your dashboard', 'error')
        return redirect(url_for('main.login'))
    
    from .models import Cart
    user_id = session['user_id']
    
    # Get actual cart count
    cart = Cart.query.filter_by(user_id=user_id).first()
    cart_count = cart.get_total_items() if cart else 0
    
    # TODO: Get actual counts from database when other models are ready
    context = {
        'cart_count': cart_count,
        'wishlist_count': 0,
        'orders_count': 0,
        'books_read': 0
    }
    return render_template('dashboard.html', **context)

@main.route('/logout')
def logout():
    """Logout route - clears session"""
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye {username}! You have been logged out successfully.', 'success')
    return redirect(url_for('main.home'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Login page route"""
    if request.method == 'GET':
        return render_template('login.html')
    
    # Handle POST request for login
    data = request.get_json() if request.is_json else request.form
    username = data.get('username')
    password = data.get('password')
    # allow login by username or email
    user = User.query.filter((User.username==username)|(User.email==username)).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.username)
        session['username'] = user.username
        session['user_id'] = user.id
        if request.is_json:
            return jsonify({'access_token': access_token}), 200
        else:
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('main.dashboard'))

    if request.is_json:
        return jsonify({'message': 'Invalid credentials'}), 401
    else:
        flash('Invalid username or password', 'error')
        return render_template('login.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page route"""
    if request.method == 'GET':
        return render_template('signup.html')
    
    # Handle POST request for registration
    data = request.get_json() if request.is_json else request.form
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm = data.get('confirm_password') or data.get('confirm')

    if not username or not email or not password:
        flash('Please fill all required fields', 'error')
        return render_template('signup.html')

    if password != confirm:
        flash('Passwords do not match', 'error')
        return render_template('signup.html')

    if User.query.filter((User.username==username)|(User.email==email)).first():
        flash('User with that username or email already exists', 'error')
        return render_template('signup.html')

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    # Auto-login after successful registration
    session['username'] = new_user.username
    session['user_id'] = new_user.id
    flash(f'Welcome to Sky Readers Haven, {new_user.username}! Your account has been created successfully.', 'success')
    return redirect(url_for('main.dashboard'))

# Shopping Cart Routes
@main.route('/cart')
def view_cart():
    """View shopping cart page"""
    if 'user_id' not in session:
        flash('Please log in to view your cart', 'error')
        return redirect(url_for('main.login'))
    
    from .models import Cart
    user_id = session['user_id']
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    context = {
        'cart': cart,
        'cart_items': cart.items if cart else [],
        'total': cart.get_total_price() if cart else 0,
        'item_count': cart.get_total_items() if cart else 0
    }
    return render_template('cart.html', **context)

@main.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    """Add a book to cart"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in to add items to cart'}), 401
    
    data = request.get_json()
    book_id = data.get('book_id')
    quantity = data.get('quantity', 1)
    
    if not book_id:
        return jsonify({'error': 'Book ID is required'}), 400
    
    try:
        from .models import Cart, CartItem, Book
        user_id = session['user_id']
        
        # Get or create cart for user
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.commit()
        
        # Check if book exists
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        # Check if item already in cart
        cart_item = CartItem.query.filter_by(cart_id=cart.id, book_id=book_id).first()
        if cart_item:
            # Update quantity
            cart_item.quantity += quantity
        else:
            # Add new item
            cart_item = CartItem(
                cart_id=cart.id,
                book_id=book_id,
                quantity=quantity,
                price=book.price
            )
            db.session.add(cart_item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{book.title} added to cart',
            'cart_count': cart.get_total_items()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while adding to cart'}), 500

@main.route('/api/cart', methods=['GET'])
def get_cart():
    """Get user's cart items"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in to view cart'}), 401
    
    try:
        from .models import Cart
        user_id = session['user_id']
        cart = Cart.query.filter_by(user_id=user_id).first()
        
        if not cart:
            return jsonify({
                'items': [],
                'total': 0,
                'item_count': 0
            }), 200
        
        items = []
        for item in cart.items:
            items.append({
                'id': item.id,
                'book_id': item.book_id,
                'book_title': item.book.title,
                'book_author': item.book.author.name if item.book.author else 'Unknown',
                'price': item.price,
                'quantity': item.quantity,
                'subtotal': item.get_subtotal()
            })
        
        return jsonify({
            'items': items,
            'total': cart.get_total_price(),
            'item_count': cart.get_total_items()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching cart'}), 500

@main.route('/api/cart/update/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    """Update cart item quantity"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in'}), 401
    
    data = request.get_json()
    quantity = data.get('quantity')
    
    if not quantity or quantity < 1:
        return jsonify({'error': 'Invalid quantity'}), 400
    
    try:
        from .models import CartItem, Cart
        user_id = session['user_id']
        
        # Verify item belongs to user's cart
        cart_item = CartItem.query.join(Cart).filter(
            CartItem.id == item_id,
            Cart.user_id == user_id
        ).first()
        
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        cart_item.quantity = quantity
        db.session.commit()
        
        cart = cart_item.cart
        return jsonify({
            'success': True,
            'message': 'Cart updated',
            'subtotal': cart_item.get_subtotal(),
            'cart_total': cart.get_total_price(),
            'cart_count': cart.get_total_items()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while updating cart'}), 500

@main.route('/api/cart/remove/<int:item_id>', methods=['DELETE'])
def remove_cart_item(item_id):
    """Remove item from cart"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in'}), 401
    
    try:
        from .models import CartItem, Cart
        user_id = session['user_id']
        
        # Verify item belongs to user's cart
        cart_item = CartItem.query.join(Cart).filter(
            CartItem.id == item_id,
            Cart.user_id == user_id
        ).first()
        
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        cart = cart_item.cart
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item removed from cart',
            'cart_total': cart.get_total_price(),
            'cart_count': cart.get_total_items()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while removing item'}), 500

@main.route('/api/cart/clear', methods=['DELETE'])
def clear_cart():
    """Clear entire cart"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in'}), 401
    
    try:
        from .models import Cart
        user_id = session['user_id']
        
        cart = Cart.query.filter_by(user_id=user_id).first()
        if cart:
            # Delete all items (cascade will handle this)
            db.session.delete(cart)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cart cleared'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while clearing cart'}), 500

@main.route('/api/book/save-from-google', methods=['POST'])
def save_book_from_google():
    """Save a Google Books API book to our database"""
    data = request.get_json()
    
    try:
        from .models import Author, Category, Book
        
        title = data.get('title')
        authors = data.get('authors', [])
        description = data.get('description', '')
        published_date = data.get('publishedDate', '')
        isbn = data.get('isbn', '')
        price = data.get('price', 9.99)  # Default price
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        # Check if book already exists by title (simple check)
        existing_book = Book.query.filter_by(title=title).first()
        if existing_book:
            return jsonify({
                'success': True,
                'book_id': existing_book.id,
                'message': 'Book already exists'
            }), 200
        
        # Get or create author (use first author)
        author_name = authors[0] if authors else 'Unknown'
        author = Author.query.filter_by(name=author_name).first()
        if not author:
            author = Author(name=author_name)
            db.session.add(author)
            db.session.flush()  # Get author.id
        
        # Get or create category (default to General)
        category = Category.query.filter_by(name='General').first()
        if not category:
            category = Category(name='General')
            db.session.add(category)
            db.session.flush()
        
        # Parse published date
        from datetime import datetime
        pub_date = None
        if published_date:
            try:
                # Try parsing year-only or full date
                if len(published_date) == 4:
                    pub_date = datetime.strptime(published_date, '%Y').date()
                else:
                    pub_date = datetime.strptime(published_date[:10], '%Y-%m-%d').date()
            except:
                pass
        
        # Create book
        new_book = Book(
            title=title,
            description=description,
            published_date=pub_date,
            isbn=isbn[:13] if isbn else None,  # Limit to 13 chars
            price=price,
            author_id=author.id,
            category_id=category.id
        )
        
        db.session.add(new_book)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'book_id': new_book.id,
            'message': 'Book saved successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving book: {e}")
        return jsonify({'error': 'An error occurred while saving book'}), 500

# API Routes (JSON-based)
@main.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'User already exists'}), 400
    new_user = User(username=data['username'], email=data['email'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@main.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.username)
        return jsonify({'access_token': access_token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@main.route('/search', methods=['GET'])
def search():
    """Search books using Google Books API and render results."""
    query = request.args.get('query')
    if not query:
        # Render books page with no results
        return render_template('books.html', books=[])

    books = search_books(query) or []

    # Convert Google Books items to a simple dict for the template
    results = []
    for item in books:
        v = item.get('volumeInfo', {})
        results.append({
            'id': item.get('id'),
            'title': v.get('title'),
            'authors': v.get('authors'),
            'description': v.get('description'),
            'publishedDate': v.get('publishedDate'),
            'image': (v.get('imageLinks') or {}).get('thumbnail')
        })

    # If the request is expecting JSON (ajax), return JSON
    if request.is_json or request.args.get('format') == 'json':
        return jsonify(results)

    return render_template('books.html', books=results)


@main.route('/book/<volume_id>')
def book_detail(volume_id):
    from .api_integration import get_book_by_id
    item = get_book_by_id(volume_id)
    if not item:
        flash('Book not found', 'error')
        return redirect(url_for('main.books'))
    v = item.get('volumeInfo', {})
    book = {
        'title': v.get('title'),
        'authors': v.get('authors'),
        'description': v.get('description'),
        'publishedDate': v.get('publishedDate'),
        'image': (v.get('imageLinks') or {}).get('thumbnail')
    }
    return render_template('book_detail.html', book=book)

@main.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    books = Book.query.all()
    books_list = [{'title': book.title, 'author': book.author.name} for book in books]
    return jsonify(books_list)


# ===========================
# CHECKOUT & ORDER ROUTES
# ===========================

@main.route('/checkout', methods=['GET'])
def checkout():
    """Display checkout page"""
    if 'user_id' not in session:
        flash('Please login to proceed to checkout', 'error')
        return redirect(url_for('main.login'))
    
    # Get user's cart
    from .models import Cart, CartItem
    cart = Cart.query.filter_by(user_id=session['user_id']).first()
    
    if not cart or not cart.items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('main.view_cart'))
    
    # Get user details for pre-filling form
    user = User.query.get(session['user_id'])
    
    return render_template('checkout.html', cart=cart, user=user)


@main.route('/checkout', methods=['POST'])
def process_checkout():
    """Process checkout and create order"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login to proceed'}), 401
    
    try:
        # Get form data
        data = request.get_json() if request.is_json else request.form
        
        # Validate required fields
        required_fields = ['shipping_name', 'shipping_email', 'shipping_phone', 
                          'shipping_address', 'shipping_city', 'shipping_state', 
                          'shipping_zip', 'shipping_country', 'payment_method']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False, 
                    'message': f'Missing required field: {field.replace("_", " ").title()}'
                }), 400
        
        # Get user's cart
        from .models import Cart, CartItem, Order, OrderItem
        cart = Cart.query.filter_by(user_id=session['user_id']).first()
        
        if not cart or not cart.items:
            return jsonify({'success': False, 'message': 'Cart is empty'}), 400
        
        # Calculate totals
        subtotal = cart.get_total()
        tax_rate = 0.08  # 8% tax rate
        tax = round(subtotal * tax_rate, 2)
        shipping_cost = 5.99 if subtotal < 50 else 0  # Free shipping over $50
        total = round(subtotal + tax + shipping_cost, 2)
        
        # Generate unique order number
        import uuid
        from datetime import datetime
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Create order
        order = Order(
            user_id=session['user_id'],
            order_number=order_number,
            status='pending',
            subtotal=subtotal,
            tax=tax,
            shipping_cost=shipping_cost,
            total=total,
            shipping_name=data.get('shipping_name'),
            shipping_email=data.get('shipping_email'),
            shipping_phone=data.get('shipping_phone'),
            shipping_address=data.get('shipping_address'),
            shipping_city=data.get('shipping_city'),
            shipping_state=data.get('shipping_state'),
            shipping_zip=data.get('shipping_zip'),
            shipping_country=data.get('shipping_country'),
            payment_method=data.get('payment_method'),
            payment_status='pending'
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items from cart items
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                book_id=cart_item.book_id,
                quantity=cart_item.quantity,
                price=cart_item.book.price
            )
            db.session.add(order_item)
        
        # Clear cart after successful order
        CartItem.query.filter_by(cart_id=cart.id).delete()
        
        db.session.commit()
        
        # Return success response
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Order placed successfully',
                'order_id': order.id,
                'order_number': order.order_number,
                'redirect': url_for('main.order_confirmation', order_id=order.id)
            })
        else:
            flash('Order placed successfully!', 'success')
            return redirect(url_for('main.order_confirmation', order_id=order.id))
    
    except Exception as e:
        db.session.rollback()
        print(f"Checkout error: {str(e)}")
        if request.is_json:
            return jsonify({'success': False, 'message': 'An error occurred processing your order'}), 500
        else:
            flash('An error occurred processing your order. Please try again.', 'error')
            return redirect(url_for('main.checkout'))


@main.route('/order/<int:order_id>')
def order_confirmation(order_id):
    """Display order confirmation page"""
    if 'user_id' not in session:
        flash('Please login to view orders', 'error')
        return redirect(url_for('main.login'))
    
    from .models import Order
    order = Order.query.filter_by(id=order_id, user_id=session['user_id']).first()
    
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('order_confirmation.html', order=order)


@main.route('/orders')
def order_history():
    """Display user's order history"""
    if 'user_id' not in session:
        flash('Please login to view orders', 'error')
        return redirect(url_for('main.login'))
    
    from .models import Order
    orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
    
    return render_template('order_history.html', orders=orders)
