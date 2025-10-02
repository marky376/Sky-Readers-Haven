// ============================================
// SKY READERS HAVEN - ENHANCED JAVASCRIPT
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all features
    initMobileMenu();
    initSearchFunctionality();
    initScrollEffects();
    initCardAnimations();
    initFormValidation();
});

// === MOBILE MENU ===
function initMobileMenu() {
    const menuIcon = document.getElementById('menu-icon');
    const navMenu = document.querySelector('.site-nav, #navmenu, .navmenu');
    
    if (menuIcon && navMenu) {
        // Toggle menu
        menuIcon.addEventListener('click', function(e) {
            e.stopPropagation();
            navMenu.classList.toggle('active');
            menuIcon.classList.toggle('active');
            
            // Change icon
            const icon = menuIcon.querySelector('i');
            if (icon) {
                if (navMenu.classList.contains('active')) {
                    icon.className = 'bx bx-x';
                } else {
                    icon.className = 'bx bx-menu';
                }
            }
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!menuIcon.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('active');
                menuIcon.classList.remove('active');
                
                const icon = menuIcon.querySelector('i');
                if (icon) {
                    icon.className = 'bx bx-menu';
                }
            }
        });

        // Close menu when clicking a link
        const navLinks = navMenu.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('active');
                menuIcon.classList.remove('active');
                
                const icon = menuIcon.querySelector('i');
                if (icon) {
                    icon.className = 'bx bx-menu';
                }
            });
        });
    }
}

// === SEARCH FUNCTIONALITY ===
function initSearchFunctionality() {
    const searchForms = document.querySelectorAll('.search-inline, #search-form');
    
    searchForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const input = form.querySelector('input[name="query"]');
            if (input && !input.value.trim()) {
                e.preventDefault();
                showNotification('Please enter a search query', 'warning');
                input.focus();
            }
        });
    });

    // Add loading state to search buttons
    const searchButtons = document.querySelectorAll('.search-inline button, #search-form button');
    searchButtons.forEach(button => {
        const form = button.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                button.disabled = true;
                button.textContent = 'Searching...';
                setTimeout(() => {
                    button.disabled = false;
                    button.textContent = 'Search';
                }, 3000);
            });
        }
    });
}

// === SCROLL EFFECTS ===
function initScrollEffects() {
    const header = document.querySelector('.site-header');
    let lastScroll = 0;

    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;

        // Add shadow on scroll
        if (currentScroll > 10) {
            if (header) header.classList.add('scrolled');
        } else {
            if (header) header.classList.remove('scrolled');
        }

        // Hide header on scroll down, show on scroll up
        if (currentScroll > lastScroll && currentScroll > 100) {
            if (header) header.style.transform = 'translateY(-100%)';
        } else {
            if (header) header.style.transform = 'translateY(0)';
        }

        lastScroll = currentScroll;
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// === CARD ANIMATIONS ===
function initCardAnimations() {
    const cards = document.querySelectorAll('.card, .feature');
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    entry.target.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 100);
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    cards.forEach(card => observer.observe(card));
}

// === FORM VALIDATION ===
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], textarea[required]');
        
        inputs.forEach(input => {
            // Add validation on blur
            input.addEventListener('blur', function() {
                validateInput(this);
            });

            // Remove error on input
            input.addEventListener('input', function() {
                if (this.classList.contains('error')) {
                    this.classList.remove('error');
                    removeErrorMessage(this);
                }
            });
        });

        // Validate on submit
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateInput(input)) {
                    isValid = false;
                }
            });

            if (!isValid) {
                e.preventDefault();
                showNotification('Please fill in all required fields correctly', 'error');
            }
        });
    });
}

function validateInput(input) {
    const value = input.value.trim();
    const type = input.type;
    let isValid = true;
    let errorMessage = '';

    // Check if empty
    if (input.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required';
    }
    // Email validation
    else if (type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
    }
    // Password validation
    else if (input.name === 'password' && value && value.length < 6) {
        isValid = false;
        errorMessage = 'Password must be at least 6 characters';
    }
    // Username validation
    else if (input.name === 'username' && value && value.length < 3) {
        isValid = false;
        errorMessage = 'Username must be at least 3 characters';
    }

    if (!isValid) {
        input.classList.add('error');
        showErrorMessage(input, errorMessage);
    } else {
        input.classList.remove('error');
        removeErrorMessage(input);
    }

    return isValid;
}

function showErrorMessage(input, message) {
    removeErrorMessage(input);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.color = '#ef4444';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '0.25rem';
    
    input.parentNode.insertBefore(errorDiv, input.nextSibling);
}

function removeErrorMessage(input) {
    const errorMessage = input.parentNode.querySelector('.error-message');
    if (errorMessage) {
        errorMessage.remove();
    }
}

// === NOTIFICATION SYSTEM ===
function showNotification(message, type) {
    if (type === void 0) type = 'info';
    
    const notification = document.createElement('div');
    notification.className = 'flash ' + type;
    notification.textContent = message;
    notification.style.cssText = '\n        position: fixed;\n        top: 20px;\n        right: 20px;\n        z-index: 9999;\n        min-width: 300px;\n        max-width: 500px;\n        animation: slideIn 0.3s ease;\n    ';

    document.body.appendChild(notification);

    setTimeout(function() {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(function() { return notification.remove(); }, 300);
    }, 5000);
}

// === BOOK DETAIL INTERACTIONS ===
function createBookElement(book) {
    const bookDiv = document.createElement('article');
    bookDiv.className = 'card';
    
    const volumeInfo = book.volumeInfo || {};
    const imageLinks = volumeInfo.imageLinks || {};
    const thumbnail = imageLinks.thumbnail || imageLinks.smallThumbnail || '/static/images/book.png';
    
    bookDiv.innerHTML = '\n        <div class="cover">\n            <img src="' + thumbnail + '" alt="' + (volumeInfo.title || 'Book') + '" loading="lazy">\n        </div>\n        <div class="meta">\n            <h3>' + (volumeInfo.title || 'Unknown Title') + '</h3>\n            <p class="authors">' + (volumeInfo.authors ? volumeInfo.authors.join(', ') : 'Unknown Author') + '</p>\n            <p class="desc">' + (volumeInfo.description ? volumeInfo.description.substring(0, 150) + '...' : 'No description available') + '</p>\n            <div class="actions">\n                <span class="published">' + (volumeInfo.publishedDate || 'N/A') + '</span>\n                <a href="/book/' + book.id + '" class="btn">Details</a>\n            </div>\n        </div>\n    ';
    
    return bookDiv;
}

// === IMAGE LAZY LOADING ===
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                }
                observer.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(function(img) {
        imageObserver.observe(img);
    });
}

// === UTILS ===
function debounce(func, wait) {
    let timeout;
    return function executedFunction() {
        const args = arguments;
        const later = function() {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = '\n    @keyframes slideOut {\n        to {\n            transform: translateX(400px);\n            opacity: 0;\n        }\n    }\n    \n    input.error, textarea.error {\n        border-color: #ef4444 !important;\n        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;\n    }\n    \n    .site-header {\n        transition: transform 0.3s ease, box-shadow 0.3s ease;\n    }\n    \n    .site-header.scrolled {\n        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);\n    }\n';
document.head.appendChild(style);

console.log('Sky Readers Haven JavaScript loaded successfully! 📚');

// ============================================
// SHOPPING CART FUNCTIONALITY
// ============================================

// Update cart badge count
function updateCartBadge() {
    fetch('/api/cart')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('cart-count');
            if (badge) {
                const count = data.item_count || 0;
                badge.textContent = count;
                if (count > 0) {
                    badge.style.display = 'block';
                } else {
                    badge.style.display = 'none';
                }
            }
        })
        .catch(error => {
            console.error('Error updating cart badge:', error);
        });
}

// Add book to cart
async function addToCart(bookId, bookTitle = 'Book') {
    // Check if user is logged in by checking if cart badge exists
    const cartBadge = document.getElementById('cart-count');
    if (!cartBadge) {
        showNotification('Please log in to add items to cart', 'error');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1500);
        return;
    }

    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                book_id: bookId,
                quantity: 1
            })
        });

        const data = await response.json();

        if (response.ok) {
            showNotification(data.message || `${bookTitle} added to cart!`, 'success');
            updateCartBadge();
        } else {
            showNotification(data.error || 'Failed to add to cart', 'error');
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        showNotification('An error occurred. Please try again.', 'error');
    }
}

// Add Google Books book to cart (saves to DB first)
async function addGoogleBookToCart(bookData, button) {
    // Check if user is logged in
    const cartBadge = document.getElementById('cart-count');
    if (!cartBadge) {
        showNotification('Please log in to add items to cart', 'error');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1500);
        return;
    }

    // Show loading state
    if (button) {
        button.classList.add('loading');
        button.disabled = true;
    }

    try {
        // First, save the Google Books book to our database
        const saveResponse = await fetch('/api/book/save-from-google', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(bookData)
        });

        const saveData = await saveResponse.json();

        if (saveResponse.ok && saveData.book_id) {
            // Now add to cart using the database book_id
            const cartResponse = await fetch('/api/cart/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    book_id: saveData.book_id,
                    quantity: 1
                })
            });

            const cartData = await cartResponse.json();

            if (cartResponse.ok) {
                showNotification(cartData.message || `${bookData.title} added to cart!`, 'success');
                updateCartBadge();
            } else {
                showNotification(cartData.error || 'Failed to add to cart', 'error');
            }
        } else {
            showNotification(saveData.error || 'Failed to save book', 'error');
        }
    } catch (error) {
        console.error('Error adding Google book to cart:', error);
        showNotification('An error occurred. Please try again.', 'error');
    } finally {
        // Remove loading state
        if (button) {
            button.classList.remove('loading');
            button.disabled = false;
        }
    }
}


// Show notification toast
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.toast-notification');
    if (existing) {
        existing.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `toast-notification toast-${type}`;
    notification.innerHTML = `
        <i class='bx ${type === 'success' ? 'bx-check-circle' : type === 'error' ? 'bx-error-circle' : 'bx-info-circle'}'></i>
        <span>${message}</span>
    `;

    document.body.appendChild(notification);

    // Trigger animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Initialize cart badge on page load
if (document.getElementById('cart-count')) {
    updateCartBadge();
}