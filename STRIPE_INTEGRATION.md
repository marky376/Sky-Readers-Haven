# Stripe Payment Integration Guide

## Overview
This document explains the Stripe payment integration implemented in Sky Readers Haven bookstore application.

## Features Implemented
✅ Stripe Elements for secure card input
✅ Payment Intent API for payment processing
✅ Real-time card validation
✅ 3D Secure (SCA) support
✅ Webhook handling for payment events
✅ Order status tracking
✅ Secure payment confirmation flow

## Setup Instructions

### 1. Get Stripe API Keys
1. Sign up for a Stripe account at https://stripe.com
2. Navigate to: Dashboard → Developers → API keys
3. You'll find two types of keys:
   - **Test keys**: For development (starts with `sk_test_` and `pk_test_`)
   - **Live keys**: For production (starts with `sk_live_` and `pk_live_`)

### 2. Configure Environment Variables
Create a `.env` file in the root directory (or copy from `.env.example`):

```bash
# Stripe Test Keys (for development)
STRIPE_SECRET_KEY=sk_test_51xxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_51xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

### 3. Install Dependencies
```bash
source venv/bin/activate
pip install stripe==7.4.0
```

### 4. Set Up Stripe Webhook (Optional for Production)
1. Go to: Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. Enter your webhook URL: `https://yourdomain.com/api/stripe/webhook`
4. Select events to listen to:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
5. Copy the webhook signing secret to `.env`

## Payment Flow

### User Journey
1. **Add items to cart** → User browses and adds books
2. **Navigate to checkout** → User clicks "Proceed to Checkout"
3. **Fill shipping info** → User enters delivery details
4. **Select payment method** → Card or PayPal
5. **Enter card details** → Stripe Elements securely captures card info
6. **Submit order** → Frontend creates order and gets PaymentIntent
7. **Confirm payment** → Stripe validates and processes payment
8. **Redirect to confirmation** → User sees order confirmation page

### Technical Flow
```
┌─────────────┐    1. Submit Order    ┌──────────────┐
│  Frontend   │ ──────────────────→  │   Backend    │
│  (checkout) │                       │   (Flask)    │
└─────────────┘                       └──────────────┘
                                            │
                                            │ 2. Create Order
                                            ├──────────→ Database
                                            │
                                            │ 3. Create PaymentIntent
                                            ├──────────→ Stripe API
                                            │
                                            │ 4. Return client_secret
                                            ↓
┌─────────────┐   5. Confirm Payment   ┌──────────────┐
│  Stripe.js  │ ←─────────────────────│   Frontend   │
│  (Elements) │                        │              │
└─────────────┘                        └──────────────┘
      │
      │ 6. Process Payment
      ↓
┌──────────────┐   7. Webhook Event    ┌──────────────┐
│  Stripe API  │ ──────────────────→  │   Backend    │
│              │                       │   (webhook)  │
└──────────────┘                       └──────────────┘
                                             │
                                             │ 8. Update Order Status
                                             ↓
                                        Database
```

## API Endpoints

### 1. GET /api/stripe/config
Returns Stripe publishable key for frontend initialization.

**Response:**
```json
{
  "publishableKey": "pk_test_xxxxxxxxxxxxx"
}
```

### 2. POST /checkout
Creates order and Stripe PaymentIntent.

**Request:**
```json
{
  "shipping_name": "John Doe",
  "shipping_email": "john@example.com",
  "shipping_phone": "(555) 123-4567",
  "shipping_address": "123 Main St",
  "shipping_city": "New York",
  "shipping_state": "NY",
  "shipping_zip": "10001",
  "shipping_country": "US",
  "payment_method": "card"
}
```

**Response (Card Payment):**
```json
{
  "success": true,
  "requiresPayment": true,
  "clientSecret": "pi_xxxxxxxxxxxxx_secret_xxxxxxxxxxxxx",
  "order_id": 123,
  "order_number": "ORD-20231002-ABCD1234"
}
```

**Response (PayPal/Other):**
```json
{
  "success": true,
  "message": "Order placed successfully",
  "order_id": 123,
  "order_number": "ORD-20231002-ABCD1234",
  "redirect": "/order/123"
}
```

### 3. POST /api/payment/confirm
Confirms payment after Stripe processing.

**Request:**
```json
{
  "payment_intent_id": "pi_xxxxxxxxxxxxx",
  "order_id": 123
}
```

**Response:**
```json
{
  "success": true,
  "message": "Payment successful",
  "redirect": "/order/123"
}
```

### 4. POST /api/stripe/webhook
Receives Stripe webhook events.

**Events Handled:**
- `payment_intent.succeeded` → Updates order to "processing"
- `payment_intent.payment_failed` → Updates order to "cancelled"

## Database Schema Updates

### Order Model Fields
```python
transaction_id = db.Column(db.String(100))  # Stripe PaymentIntent ID
payment_status = db.Column(db.String(20))   # pending/processing/completed/failed
payment_method = db.Column(db.String(50))   # card/paypal
status = db.Column(db.String(20))           # pending/processing/shipped/delivered/cancelled
```

## Frontend Integration

### Stripe Elements Initialization
```javascript
// Load Stripe.js
const stripe = Stripe('pk_test_xxxxxxxxxxxxx');
const elements = stripe.elements();
const cardElement = elements.create('card');
cardElement.mount('#card-element');
```

### Payment Confirmation
```javascript
const {error, paymentIntent} = await stripe.confirmCardPayment(
  clientSecret,
  {
    payment_method: {
      card: cardElement,
      billing_details: { /* shipping info */ }
    }
  }
);
```

## Testing

### Test Card Numbers
Stripe provides test cards for development:

| Card Number          | Description                    |
|---------------------|--------------------------------|
| 4242 4242 4242 4242 | Successful payment             |
| 4000 0025 0000 3155 | 3D Secure authentication       |
| 4000 0000 0000 9995 | Declined (insufficient funds)  |
| 4000 0000 0000 0002 | Declined (card declined)       |

**All test cards:**
- Use any future expiration date (e.g., 12/34)
- Use any 3-digit CVC (e.g., 123)
- Use any ZIP code (e.g., 12345)

### Testing Webhooks Locally
Use Stripe CLI to forward webhook events to your local server:

```bash
# Install Stripe CLI
# Download from: https://stripe.com/docs/stripe-cli

# Login to Stripe
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:5000/api/stripe/webhook

# Trigger test events
stripe trigger payment_intent.succeeded
stripe trigger payment_intent.payment_failed
```

## Security Best Practices

✅ **Never expose secret keys** - Always use environment variables
✅ **Validate webhooks** - Use webhook signatures to verify authenticity
✅ **Use HTTPS in production** - Stripe requires SSL/TLS
✅ **Sanitize user input** - Validate all form data
✅ **Log payment events** - Track all payment attempts
✅ **Handle errors gracefully** - Show user-friendly error messages
✅ **Use SCA-ready integration** - Support 3D Secure authentication

## Error Handling

### Common Errors

**1. Card Declined**
```python
stripe.error.CardError: 
"Your card was declined"
```
**Solution**: Ask user to try a different card or payment method

**2. Invalid API Key**
```python
stripe.error.AuthenticationError: 
"Invalid API Key provided"
```
**Solution**: Check `.env` file and ensure correct API key

**3. Payment Intent Not Found**
```python
stripe.error.InvalidRequestError: 
"No such payment_intent"
```
**Solution**: Verify payment_intent_id is correct and not expired

## Payment Status States

### Order Status Flow
```
pending → processing → shipped → delivered
   ↓
cancelled (if payment fails)
```

### Payment Status Flow
```
pending → processing → completed
   ↓
failed (card declined or error)
```

## Production Checklist

- [ ] Replace test keys with live keys in `.env`
- [ ] Set up production webhook endpoint
- [ ] Configure webhook signing secret
- [ ] Enable HTTPS on your domain
- [ ] Test payment flow with real cards
- [ ] Set up Stripe Radar for fraud prevention
- [ ] Configure email notifications
- [ ] Add proper logging and monitoring
- [ ] Test error scenarios
- [ ] Update terms of service with payment info

## Monitoring

### Stripe Dashboard
Monitor payments in real-time:
- Dashboard → Payments → All payments
- View successful, failed, and disputed payments
- Track revenue and transaction history

### Application Logs
Monitor application logs for:
- Payment intent creation
- Payment confirmation
- Webhook events
- Error messages

## Support

### Stripe Documentation
- API Reference: https://stripe.com/docs/api
- Testing Guide: https://stripe.com/docs/testing
- Webhook Guide: https://stripe.com/docs/webhooks

### Troubleshooting
If you encounter issues:
1. Check Stripe logs in Dashboard → Developers → Logs
2. Verify API keys are correct
3. Test with Stripe's test cards
4. Check webhook endpoint is accessible
5. Review application logs for errors

## Future Enhancements

- [ ] Add support for Apple Pay / Google Pay
- [ ] Implement subscription payments for premium features
- [ ] Add refund functionality
- [ ] Support multiple currencies
- [ ] Implement payment method storage for returning customers
- [ ] Add installment payment options
- [ ] Integrate with accounting software
