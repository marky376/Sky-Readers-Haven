Sky Readers Haven
Project Overview
Sky Readers Haven is an innovative online bookstore designed to offer a seamless and enjoyable reading experience for book lovers. This document provides a comprehensive architectural overview of the system, detailing various components and their interactions.

Architecture
The architecture of Sky Readers Haven is built using Flask as a full-stack web framework, providing both backend API functionality and frontend template rendering.

Overview Diagram
(Include a high-level diagram here depicting the components and their interactions.)

Frontend: Flask Jinja2 templates with HTML, CSS, and JavaScript for the user interface.
Backend: Flask web framework with RESTful API endpoints.
Database: SQLite (development) / PostgreSQL (production) for data storage.
External APIs: Google Books API for book catalog integration.
Cloud: AWS for deployment and scalability.
Component Breakdown
Frontend: Flask Jinja2 templates handle user interaction and display data from the backend.
Backend: Flask processes requests, interacts with the database, and serves both web pages and API responses.
Database: SQLAlchemy ORM stores user data, book information, and transaction records.
External Services: Google Books API provides comprehensive book catalog data.
Cloud Services: Hosts the application, provides storage solutions, and manages load balancing.
APIs and Methods
Sky Readers Haven utilizes both traditional web routes for page rendering and RESTful API endpoints for dynamic functionality. Below are some of the key endpoints:

Authentication
POST /signup: Registers a new user with email confirmation.

Request: Form data { "name": "string", "email": "string", "password": "string", "confirm_password": "string" }
Response: Redirects to confirmation page or renders signup form with errors
POST /login: Authenticates a user and creates a session.

Request: Form data { "username": "string", "password": "string" }
Response: JWT token and redirect to dashboard or login form with errors
Book Search
GET /search: Searches books using Google Books API (requires authentication).

Request: Query parameter ?query=search_term
Response: JSON array of book results from Google Books API
Shopping Cart
POST /api/cart: Adds a book to the cart.

Request: { "book_id": "int", "quantity": "int" }
Response: { "message": "Book added to cart." }
GET /api/cart: Retrieves the current user's cart.

Response: [ { "book_id": "int", "title": "string", "quantity": "int", "price": "float" }, ... ]
Orders
POST /api/orders: Creates a new order from the cart.
Request: { "cart_id": "int", "payment_method": "string" }
Response: { "message": "Order placed successfully." }
Data Modeling
Data in Sky Readers Haven is structured and managed using PostgreSQL. Below are the primary tables and their relationships:

User Table
id: Primary Key
username: String
password: String (hashed)
email: String
Book Table
id: Primary Key
title: String
author: String
price: Float
description: Text
Cart Table
id: Primary Key
user_id: Foreign Key (references User)
created_at: Timestamp
CartItem Table
id: Primary Key
cart_id: Foreign Key (references Cart)
book_id: Foreign Key (references Book)
quantity: Integer
Order Table
id: Primary Key
user_id: Foreign Key (references User)
total_amount: Float
status: String
created_at: Timestamp
User Stories
As a user, I want to register and create an account so that I can log in and make purchases.
As a user, I want to browse books by category so that I can find books I like.
As a user, I want to add books to my shopping cart so that I can purchase them later.
As a user, I want to place an order for the books in my cart so that I can buy them.
As an admin, I want to add and manage book listings so that users can see the available books.
Mockups
(Include mockups here. You can use tools like Figma or Sketch to create visual representations of the pages, such as the homepage, book detail page, cart, and checkout process.)

Cloud Services
We are considering using Microsoft Azure or AWS Cloud for the project.

AWS
EC2: For hosting the backend server.
S3: For storing static assets like book images.
RDS: For managing the PostgreSQL database.
CloudFront: For CDN to speed up content delivery.
Azure
Azure App Service: For hosting the backend server.
Azure Blob Storage: For storing static assets.
Azure SQL Database: For managing the PostgreSQL database.
Azure CDN: For content delivery.
Progress
Initial Planning: Completed
Architecture Design: In Progress
Backend Setup: Pending
Frontend Development: Pending
Database Design: In Progress
API Development: Pending
Testing and Debugging: Pending
Deployment: Pending
Future Plans
Feature Enhancements: Adding advanced search, reviews and ratings, recommendations.
Mobile App: Developing a mobile version of the store.
Marketing: Implementing marketing strategies to attract users.
Partnerships: Partnering with publishers and authors for exclusive releases and promotions.
About the Developer
Growing up, I always had a knack for solving complex problems, whether it was fixing a broken gadget or tackling a tough math problem. This passion for challenges was further honed at ALX SE, where I embraced the mantra of "doing hard things." This philosophy drove me to push the boundaries of my capabilities and continuously seek out new challenges.

The idea for Sky Readers Haven was born out of this same spirit. I saw the lack of a user-friendly, comprehensive online bookstore as a challenge waiting to be conquered. Building this platform from scratch required not only technical skills but also creativity and perseverance. From designing an intuitive user interface to implementing a robust backend system, every step was a test of my abilities.

One of the most challenging aspects was integrating the email confirmation system. Initially, I underestimated the complexity of this task. The first hurdle was setting up Flask-Mail and configuring it correctly to work with my SMTP server. Despite following the documentation, I encountered numerous issues with email delivery and server authentication. Debugging these problems required delving deep into the server logs and understanding the nuances of email protocols. The process was further complicated by intermittent issues with the email provider's reliability. To resolve this, I had to implement robust error handling and retries to ensure emails were sent consistently. This challenge not only tested my technical skills but also taught me the value of patience and meticulous debugging. Ultimately, overcoming this hurdle significantly enhanced my understanding of backend systems and email services.

