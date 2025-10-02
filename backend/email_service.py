"""
Email service for Sky Readers Haven
Handles all email notifications including order confirmations, receipts, etc.
"""
from flask_mail import Mail, Message
from flask import current_app, render_template_string
import os

mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail with app"""
    mail.init_app(app)

def send_order_confirmation_email(order, user):
    """Send order confirmation email to customer"""
    try:
        subject = f"Order Confirmation - {order.order_number}"
        
        # Create HTML email body
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .content {{
            background: #f9f9f9;
            padding: 30px;
            border: 1px solid #ddd;
        }}
        .order-info {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .order-info h2 {{
            color: #667eea;
            margin-top: 0;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .info-label {{
            font-weight: bold;
            color: #555;
        }}
        .info-value {{
            color: #333;
        }}
        .items-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}
        .items-table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        .items-table td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}
        .items-table tr:last-child td {{
            border-bottom: none;
        }}
        .total-row {{
            background: #f5f5f5;
            font-weight: bold;
            font-size: 18px;
        }}
        .total-row td {{
            padding: 15px 12px;
            border-top: 2px solid #667eea;
        }}
        .status-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }}
        .status-pending {{
            background: #fef3c7;
            color: #92400e;
        }}
        .status-processing {{
            background: #dbeafe;
            color: #1e40af;
        }}
        .shipping-info {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 14px;
            background: #f9f9f9;
            border-radius: 0 0 10px 10px;
            border: 1px solid #ddd;
            border-top: none;
        }}
        .button {{
            display: inline-block;
            padding: 12px 30px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            font-weight: bold;
        }}
        .button:hover {{
            background: #5568d3;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 Order Confirmed!</h1>
        <p style="margin: 10px 0 0 0; font-size: 16px;">Thank you for your purchase at Sky Readers Haven</p>
    </div>
    
    <div class="content">
        <p>Hi {user.username},</p>
        <p>Great news! Your order has been confirmed and is being processed. Here are your order details:</p>
        
        <div class="order-info">
            <h2>Order Information</h2>
            <div class="info-row">
                <span class="info-label">Order Number:</span>
                <span class="info-value">{order.order_number}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Order Date:</span>
                <span class="info-value">{order.created_at.strftime('%B %d, %Y at %I:%M %p')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Status:</span>
                <span class="info-value">
                    <span class="status-badge status-{order.status}">{order.status.upper()}</span>
                </span>
            </div>
            <div class="info-row">
                <span class="info-label">Payment Method:</span>
                <span class="info-value">{order.payment_method.upper()}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Payment Status:</span>
                <span class="info-value">{order.payment_status.upper()}</span>
            </div>
        </div>

        <div class="order-info">
            <h2>Order Items</h2>
            <table class="items-table">
                <thead>
                    <tr>
                        <th>Book Title</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''
                    <tr>
                        <td>{item.book.title}<br><small style="color: #666;">by {item.book.author.name}</small></td>
                        <td>{item.quantity}</td>
                        <td>${item.price:.2f}</td>
                        <td>${item.get_subtotal():.2f}</td>
                    </tr>
                    ''' for item in order.items])}
                    <tr>
                        <td colspan="3" style="text-align: right; font-weight: bold;">Subtotal:</td>
                        <td>${order.subtotal:.2f}</td>
                    </tr>
                    <tr>
                        <td colspan="3" style="text-align: right; font-weight: bold;">Tax (8%):</td>
                        <td>${order.tax:.2f}</td>
                    </tr>
                    <tr>
                        <td colspan="3" style="text-align: right; font-weight: bold;">Shipping:</td>
                        <td>${order.shipping_cost:.2f if order.shipping_cost > 0 else 'FREE'}</td>
                    </tr>
                    <tr class="total-row">
                        <td colspan="3" style="text-align: right;">TOTAL:</td>
                        <td>${order.total:.2f}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="shipping-info">
            <h2 style="color: #667eea; margin-top: 0; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
                Shipping Address
            </h2>
            <p style="margin: 5px 0;"><strong>{order.shipping_name}</strong></p>
            <p style="margin: 5px 0;">{order.shipping_address}</p>
            <p style="margin: 5px 0;">{order.shipping_city}, {order.shipping_state} {order.shipping_zip}</p>
            <p style="margin: 5px 0;">{order.shipping_country}</p>
            <p style="margin: 15px 0 5px 0;"><strong>Contact:</strong></p>
            <p style="margin: 5px 0;">Email: {order.shipping_email}</p>
            <p style="margin: 5px 0;">Phone: {order.shipping_phone}</p>
        </div>

        <div style="text-align: center;">
            <a href="http://localhost:5000/order/{order.id}" class="button">View Order Details</a>
        </div>

        <p style="margin-top: 30px;">
            <strong>What's Next?</strong><br>
            We'll send you another email when your order ships with tracking information.
            You can also track your order status anytime by visiting your order history.
        </p>

        <p>
            If you have any questions about your order, feel free to contact us at 
            <a href="mailto:support@skyreadershaven.com">support@skyreadershaven.com</a>
        </p>

        <p style="margin-top: 30px;">
            Thank you for shopping with us!<br>
            <strong>Sky Readers Haven Team</strong>
        </p>
    </div>

    <div class="footer">
        <p style="margin: 5px 0;">Sky Readers Haven - Your Gateway to Literary Adventures</p>
        <p style="margin: 5px 0; font-size: 12px;">
            This is an automated email. Please do not reply to this message.
        </p>
        <p style="margin: 5px 0; font-size: 12px;">
            © 2025 Sky Readers Haven. All rights reserved.
        </p>
    </div>
</body>
</html>
        """
        
        # Create plain text version
        text_body = f"""
Order Confirmation - {order.order_number}

Hi {user.username},

Thank you for your order! Here are your order details:

ORDER INFORMATION
-----------------
Order Number: {order.order_number}
Order Date: {order.created_at.strftime('%B %d, %Y at %I:%M %p')}
Status: {order.status.upper()}
Payment Method: {order.payment_method.upper()}
Payment Status: {order.payment_status.upper()}

ORDER ITEMS
-----------
{''.join([f"{item.book.title} by {item.book.author.name}\nQuantity: {item.quantity} x ${item.price:.2f} = ${item.get_subtotal():.2f}\n\n" for item in order.items])}
Subtotal: ${order.subtotal:.2f}
Tax (8%): ${order.tax:.2f}
Shipping: ${'FREE' if order.shipping_cost == 0 else f'{order.shipping_cost:.2f}'}
-----------
TOTAL: ${order.total:.2f}

SHIPPING ADDRESS
----------------
{order.shipping_name}
{order.shipping_address}
{order.shipping_city}, {order.shipping_state} {order.shipping_zip}
{order.shipping_country}

Contact:
Email: {order.shipping_email}
Phone: {order.shipping_phone}

We'll send you another email when your order ships with tracking information.
You can track your order status at: http://localhost:5000/order/{order.id}

Thank you for shopping with Sky Readers Haven!

---
Sky Readers Haven - Your Gateway to Literary Adventures
This is an automated email. Please do not reply to this message.
        """
        
        # Create and send message
        msg = Message(
            subject=subject,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@skyreadershaven.com'),
            recipients=[order.shipping_email],
            body=text_body,
            html=html_body
        )
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error sending order confirmation email: {str(e)}")
        return False


def send_payment_receipt_email(order, user):
    """Send payment receipt email"""
    try:
        subject = f"Payment Receipt - {order.order_number}"
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: #10b981;
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background: #f9f9f9;
            padding: 30px;
            border: 1px solid #ddd;
        }}
        .receipt-box {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .amount {{
            font-size: 36px;
            font-weight: bold;
            color: #10b981;
            text-align: center;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>✅ Payment Successful</h1>
        <p>Your payment has been processed successfully</p>
    </div>
    
    <div class="content">
        <p>Hi {user.username},</p>
        <p>This email confirms that we have received your payment for order <strong>{order.order_number}</strong>.</p>
        
        <div class="amount">
            ${order.total:.2f}
        </div>
        
        <div class="receipt-box">
            <h3>Payment Details</h3>
            <p><strong>Transaction ID:</strong> {order.transaction_id or 'N/A'}</p>
            <p><strong>Payment Method:</strong> {order.payment_method.upper()}</p>
            <p><strong>Payment Date:</strong> {order.updated_at.strftime('%B %d, %Y at %I:%M %p')}</p>
            <p><strong>Order Number:</strong> {order.order_number}</p>
        </div>
        
        <p>Your order is now being processed and will be shipped soon.</p>
        
        <p>Thank you for your business!</p>
    </div>
    
    <div class="footer">
        <p>Sky Readers Haven</p>
        <p style="font-size: 12px;">This is an automated receipt. Please save for your records.</p>
    </div>
</body>
</html>
        """
        
        msg = Message(
            subject=subject,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@skyreadershaven.com'),
            recipients=[order.shipping_email],
            html=html_body
        )
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error sending payment receipt email: {str(e)}")
        return False


def send_shipping_notification_email(order, user, tracking_number=None):
    """Send shipping notification email"""
    try:
        subject = f"Your Order Has Shipped - {order.order_number}"
        
        tracking_html = ''
        if tracking_number:
            tracking_html = f"""
            <div style="background: #fef3c7; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 0;"><strong>Tracking Number:</strong> {tracking_number}</p>
            </div>
            """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: #3b82f6;
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background: #f9f9f9;
            padding: 30px;
            border: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📦 Your Order Has Shipped!</h1>
        <p>Order {order.order_number} is on its way</p>
    </div>
    
    <div class="content">
        <p>Hi {user.username},</p>
        <p>Great news! Your order has been shipped and is on its way to you.</p>
        
        {tracking_html}
        
        <p><strong>Estimated Delivery:</strong> 3-5 business days</p>
        
        <p><strong>Shipping Address:</strong><br>
        {order.shipping_name}<br>
        {order.shipping_address}<br>
        {order.shipping_city}, {order.shipping_state} {order.shipping_zip}</p>
        
        <p>Thank you for your patience!</p>
    </div>
</body>
</html>
        """
        
        msg = Message(
            subject=subject,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@skyreadershaven.com'),
            recipients=[order.shipping_email],
            html=html_body
        )
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error sending shipping notification email: {str(e)}")
        return False
