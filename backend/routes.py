from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_jwt_extended import create_access_token, jwt_required
from .app import db
from .models import User, Book
from werkzeug.security import generate_password_hash, check_password_hash
from .api_integration import search_books
from .email_service import send_order_confirmation_email, send_payment_receipt_email, send_shipping_notification_email
import json

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
        session['is_admin'] = user.is_admin  # Add admin status to session
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
        
        db.session.commit()
        
        # For Stripe payments, create payment intent
        if data.get('payment_method') == 'card':
            import stripe
            from flask import current_app
            
            stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
            
            try:
                # Create Stripe PaymentIntent
                intent = stripe.PaymentIntent.create(
                    amount=int(total * 100),  # Convert to cents
                    currency='usd',
                    metadata={
                        'order_id': order.id,
                        'order_number': order.order_number,
                        'user_id': session['user_id']
                    },
                    description=f"Order {order.order_number}",
                    receipt_email=data.get('shipping_email')
                )
                
                # Store payment intent ID
                order.transaction_id = intent.id
                db.session.commit()
                
                # Return client secret for frontend
                return jsonify({
                    'success': True,
                    'requiresPayment': True,
                    'clientSecret': intent.client_secret,
                    'order_id': order.id,
                    'order_number': order.order_number
                })
            
            except stripe.error.StripeError as e:
                # Payment failed, mark order as failed
                order.payment_status = 'failed'
                db.session.commit()
                return jsonify({
                    'success': False, 
                    'message': f'Payment processing failed: {str(e)}'
                }), 400
        
        else:
            # For PayPal or other methods, clear cart and redirect
            CartItem.query.filter_by(cart_id=cart.id).delete()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Order placed successfully',
                'order_id': order.id,
                'order_number': order.order_number,
                'redirect': url_for('main.order_confirmation', order_id=order.id)
            })
    
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


# ===========================
# STRIPE PAYMENT ROUTES
# ===========================

@main.route('/api/stripe/config', methods=['GET'])
def get_stripe_config():
    """Return Stripe publishable key"""
    from flask import current_app
    return jsonify({
        'publishableKey': current_app.config['STRIPE_PUBLISHABLE_KEY']
    })


@main.route('/api/payment/confirm', methods=['POST'])
def confirm_payment():
    """Confirm payment after Stripe processing"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')
        order_id = data.get('order_id')
        
        if not payment_intent_id or not order_id:
            return jsonify({'success': False, 'message': 'Missing required data'}), 400
        
        # Verify the payment intent with Stripe
        import stripe
        from flask import current_app
        
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Get order
            from .models import Order, Cart, CartItem
            order = Order.query.filter_by(id=order_id, user_id=session['user_id']).first()
            
            if not order:
                return jsonify({'success': False, 'message': 'Order not found'}), 404
            
            # Update order based on payment status
            if intent.status == 'succeeded':
                order.payment_status = 'completed'
                order.status = 'processing'
                order.transaction_id = payment_intent_id
                
                # Clear cart
                cart = Cart.query.filter_by(user_id=session['user_id']).first()
                if cart:
                    CartItem.query.filter_by(cart_id=cart.id).delete()
                
                db.session.commit()
                
                # Send confirmation and receipt emails
                try:
                    user = User.query.get(session['user_id'])
                    send_order_confirmation_email(order, user)
                    send_payment_receipt_email(order, user)
                except Exception as e:
                    print(f"Error sending emails: {str(e)}")
                
                return jsonify({
                    'success': True,
                    'message': 'Payment successful',
                    'redirect': url_for('main.order_confirmation', order_id=order.id)
                })
            
            elif intent.status == 'processing':
                order.payment_status = 'processing'
                db.session.commit()
                return jsonify({
                    'success': True,
                    'message': 'Payment is processing',
                    'redirect': url_for('main.order_confirmation', order_id=order.id)
                })
            
            else:
                order.payment_status = 'failed'
                order.status = 'cancelled'
                db.session.commit()
                return jsonify({
                    'success': False,
                    'message': 'Payment failed. Please try again.'
                }), 400
        
        except stripe.error.StripeError as e:
            return jsonify({
                'success': False,
                'message': f'Payment verification failed: {str(e)}'
            }), 400
    
    except Exception as e:
        db.session.rollback()
        print(f"Payment confirmation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred confirming payment'
        }), 500


@main.route('/api/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    import stripe
    from flask import current_app
    
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        else:
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
    
    except ValueError as e:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        handle_payment_success(payment_intent)
    
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        handle_payment_failure(payment_intent)
    
    return jsonify({'success': True})


def handle_payment_success(payment_intent):
    """Handle successful payment"""
    try:
        from .models import Order, Cart, CartItem
        
        order_id = payment_intent.metadata.get('order_id')
        if not order_id:
            return
        
        order = Order.query.get(order_id)
        if order:
            order.payment_status = 'completed'
            order.status = 'processing'
            order.transaction_id = payment_intent.id
            
            # Clear user's cart
            cart = Cart.query.filter_by(user_id=order.user_id).first()
            if cart:
                CartItem.query.filter_by(cart_id=cart.id).delete()
            
            db.session.commit()
            
            # Send confirmation email
            try:
                user = User.query.get(order.user_id)
                send_order_confirmation_email(order, user)
                send_payment_receipt_email(order, user)
                print(f"Payment succeeded and emails sent for order {order.order_number}")
            except Exception as email_error:
                print(f"Error sending emails: {str(email_error)}")
    
    except Exception as e:
        print(f"Error handling payment success: {str(e)}")
        db.session.rollback()


def handle_payment_failure(payment_intent):
    """Handle failed payment"""
    try:
        from .models import Order
        
        order_id = payment_intent.metadata.get('order_id')
        if not order_id:
            return
        
        order = Order.query.get(order_id)
        if order:
            order.payment_status = 'failed'
            order.status = 'cancelled'
            db.session.commit()
            
            # TODO: Send failure notification email
            print(f"Payment failed for order {order.order_number}")
    
    except Exception as e:
        print(f"Error handling payment failure: {str(e)}")
        db.session.rollback()


# ===========================
# ADMIN ROUTES
# ===========================

def admin_required(f):
    """Decorator to check if user is admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access admin panel', 'error')
            return redirect(url_for('main.login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.home'))
        
        return f(*args, **kwargs)
    return decorated_function


@main.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with order management"""
    from .models import Order
    from sqlalchemy import func
    
    # Get all orders
    orders = Order.query.order_by(Order.created_at.desc()).all()
    
    # Calculate stats
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    processing_orders = Order.query.filter_by(status='processing').count()
    
    # Calculate total revenue (completed payments only)
    total_revenue = db.session.query(func.sum(Order.total)).filter(
        Order.payment_status == 'completed'
    ).scalar() or 0
    
    return render_template('admin_dashboard.html',
                         orders=orders,
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         processing_orders=processing_orders,
                         total_revenue=total_revenue)


@main.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
@admin_required
def update_order_status(order_id):
    """Update order status"""
    try:
        from .models import Order
        
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'success': False, 'message': 'Status is required'}), 400
        
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        old_status = order.status
        order.status = new_status
        db.session.commit()
        
        # Send shipping notification if order is marked as shipped
        if new_status == 'shipped' and old_status != 'shipped':
            try:
                user = User.query.get(order.user_id)
                send_shipping_notification_email(order, user)
            except Exception as e:
                print(f"Error sending shipping email: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': f'Order status updated to {new_status}',
            'order': {
                'id': order.id,
                'status': order.status
            }
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error updating order status: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500


@main.route('/api/admin/orders/<int:order_id>')
@admin_required
def get_order_details(order_id):
    """Get detailed order information"""
    try:
        from .models import Order
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        return jsonify({
            'success': True,
            'order': {
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'payment_status': order.payment_status,
                'payment_method': order.payment_method,
                'shipping_name': order.shipping_name,
                'shipping_email': order.shipping_email,
                'shipping_phone': order.shipping_phone,
                'shipping_address': order.shipping_address,
                'shipping_city': order.shipping_city,
                'shipping_state': order.shipping_state,
                'shipping_zip': order.shipping_zip,
                'shipping_country': order.shipping_country,
                'subtotal': float(order.subtotal),
                'tax': float(order.tax),
                'shipping_cost': float(order.shipping_cost),
                'total': float(order.total),
                'items': [{
                    'book_title': item.book.title,
                    'quantity': item.quantity,
                    'price': float(item.price),
                    'subtotal': float(item.get_subtotal())
                } for item in order.items]
            }
        })
    
    except Exception as e:
        print(f"Error getting order details: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500


@main.route('/api/admin/orders/export')
@admin_required
def export_orders():
    """Export orders to CSV"""
    try:
        from .models import Order
        import csv
        from io import StringIO
        from flask import Response
        
        orders = Order.query.order_by(Order.created_at.desc()).all()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Order Number', 'Customer Name', 'Email', 'Date', 
            'Status', 'Payment Status', 'Payment Method',
            'Items', 'Subtotal', 'Tax', 'Shipping', 'Total'
        ])
        
        # Write data
        for order in orders:
            writer.writerow([
                order.order_number,
                order.shipping_name,
                order.shipping_email,
                order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                order.status,
                order.payment_status,
                order.payment_method,
                len(order.items),
                f"${order.subtotal:.2f}",
                f"${order.tax:.2f}",
                f"${order.shipping_cost:.2f}",
                f"${order.total:.2f}"
            ])
        
        # Create response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=orders_export.csv'}
        )
    
    except Exception as e:
        print(f"Error exporting orders: {str(e)}")
        flash('Error exporting orders', 'error')
        return redirect(url_for('main.admin_dashboard'))


@main.route('/admin/orders/<int:order_id>/print')
@admin_required
def print_order(order_id):
    """Print-friendly order page"""
    from .models import Order
    
    order = Order.query.get(order_id)
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('main.admin_dashboard'))
    
    return render_template('print_order.html', order=order)


# ============================================================================
# USER PROFILE ROUTES
# ============================================================================

@main.route('/profile')
def profile():
    """User profile page"""
    if 'user_id' not in session:
        flash('Please log in to view your profile', 'warning')
        return redirect(url_for('main.login'))
    
    from .models import User, Order, OrderItem, Review
    from sqlalchemy import func
    
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('main.logout'))
    
    # Get user statistics
    order_count = Order.query.filter_by(user_id=user.id).count()
    
    # Calculate total spent
    total_spent_result = db.session.query(
        func.sum(Order.total_amount)
    ).filter(
        Order.user_id == user.id,
        Order.payment_status == 'paid'
    ).scalar()
    total_spent = float(total_spent_result) if total_spent_result else 0.0
    
    # Calculate items purchased
    items_purchased_result = db.session.query(
        func.sum(OrderItem.quantity)
    ).join(Order).filter(
        Order.user_id == user.id,
        Order.payment_status == 'paid'
    ).scalar()
    items_purchased = int(items_purchased_result) if items_purchased_result else 0
    
    # Get review count
    review_count = Review.query.filter_by(user_id=user.id).count()
    
    return render_template('profile.html',
                         user=user,
                         order_count=order_count,
                         total_spent=total_spent,
                         items_purchased=items_purchased,
                         review_count=review_count)


@main.route('/api/profile/update', methods=['PUT'])
def update_profile():
    """Update user profile information"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    from .models import User
    
    data = request.get_json()
    user = User.query.get(session['user_id'])
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    # Validate username
    if 'username' in data:
        username = data['username'].strip()
        if not username:
            return jsonify({'success': False, 'message': 'Username cannot be empty'}), 400
        
        # Check if username is taken by another user
        existing = User.query.filter(User.username == username, User.id != user.id).first()
        if existing:
            return jsonify({'success': False, 'message': 'Username already taken'}), 400
        
        user.username = username
        session['username'] = username  # Update session
    
    # Validate email
    if 'email' in data:
        email = data['email'].strip().lower()
        if not email:
            return jsonify({'success': False, 'message': 'Email cannot be empty'}), 400
        
        # Basic email validation
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        # Check if email is taken by another user
        existing = User.query.filter(User.email == email, User.id != user.id).first()
        if existing:
            return jsonify({'success': False, 'message': 'Email already taken'}), 400
        
        user.email = email
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error updating profile: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to update profile'}), 500


@main.route('/api/profile/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    from .models import User
    import bcrypt
    
    data = request.get_json()
    user = User.query.get(session['user_id'])
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    # Validate required fields
    if not all(k in data for k in ['current_password', 'new_password', 'confirm_password']):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # Verify current password
    if not bcrypt.checkpw(data['current_password'].encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400
    
    # Validate new password
    if len(data['new_password']) < 6:
        return jsonify({'success': False, 'message': 'New password must be at least 6 characters'}), 400
    
    if data['new_password'] != data['confirm_password']:
        return jsonify({'success': False, 'message': 'New passwords do not match'}), 400
    
    # Don't allow same password
    if data['current_password'] == data['new_password']:
        return jsonify({'success': False, 'message': 'New password must be different from current password'}), 400
    
    # Hash and update password
    hashed_password = bcrypt.hashpw(data['new_password'].encode('utf-8'), bcrypt.gensalt())
    user.password = hashed_password.decode('utf-8')
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Password changed successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error changing password: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to change password'}), 500


@main.route('/api/profile/delete', methods=['DELETE'])
def delete_account():
    """Delete user account and all associated data"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    from .models import User, Order, Cart, Review, ContactMessage
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    # Don't allow admin to delete their account if they're the only admin
    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            return jsonify({
                'success': False, 
                'message': 'Cannot delete the only admin account'
            }), 400
    
    try:
        # Delete associated data (CASCADE should handle most of this, but being explicit)
        # Orders and order items will cascade delete
        # Cart and cart items will cascade delete
        Review.query.filter_by(user_id=user_id).delete()
        ContactMessage.query.filter_by(user_id=user_id).delete()
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        # Clear session
        session.clear()
        
        return jsonify({'success': True, 'message': 'Account deleted successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting account: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to delete account'}), 500

