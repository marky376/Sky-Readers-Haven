# 🧪 Shopping Cart Testing Guide

**Phase 5 Testing Checklist**  
**Date**: October 2, 2025

---

## 🚀 Quick Start Testing

### Prerequisites
1. Server is running: `http://127.0.0.1:5000`
2. You have a user account (or create one)
3. Chrome/Firefox browser recommended

---

## 📋 Test Scenarios

### 1. Cart Badge Test
**Goal**: Verify cart icon shows correct item count

**Steps**:
1. ✅ Open homepage
2. ✅ Notice no cart icon (not logged in)
3. ✅ Click "Login" and log in
4. ✅ Notice cart icon appears in navigation with badge showing "0"
5. ✅ Badge should be hidden when count is 0

**Expected**: Cart icon visible only when logged in

---

### 2. Add to Cart Test (Not Logged In)
**Goal**: Verify login requirement works

**Steps**:
1. ✅ Log out if logged in
2. ✅ Go to "Books" page
3. ✅ Search for a book (e.g., "Harry Potter")
4. ✅ Click "Add to Cart" on any book
5. ✅ Should see error toast: "Please log in to add items to cart"
6. ✅ Should redirect to login page after 1.5 seconds

**Expected**: User cannot add to cart when not logged in

---

### 3. Add to Cart Test (Logged In)
**Goal**: Verify adding books works

**Steps**:
1. ✅ Log in to your account
2. ✅ Go to "Books" page
3. ✅ Click search bar and search for "Python programming"
4. ✅ Wait for results to load
5. ✅ Click "Add to Cart" on first book
6. ✅ Should see button show loading spinner briefly
7. ✅ Should see green success toast: "[Book Title] added to cart!"
8. ✅ Cart badge should update to "1"
9. ✅ Add another book
10. ✅ Cart badge should update to "2"

**Expected**: Books added successfully, badge updates in real-time

---

### 4. View Cart Test
**Goal**: Verify cart page displays items correctly

**Steps**:
1. ✅ After adding books (from Test 3)
2. ✅ Click cart icon in navigation
3. ✅ Should see cart page with:
   - Cart hero section
   - List of books you added
   - Each book shows: image, title, author, price
   - Quantity selectors (+ and - buttons)
   - "Remove" button for each item
   - Cart summary on right side
   - Subtotal, shipping (FREE), tax (10%), total
4. ✅ Verify total is calculated correctly

**Expected**: All cart items displayed with correct information

---

### 5. Update Quantity Test
**Goal**: Verify quantity changes work

**Steps**:
1. ✅ On cart page
2. ✅ Find a book and click the "+" button
3. ✅ Page should reload
4. ✅ Quantity should increase by 1
5. ✅ Subtotal for that item should update
6. ✅ Cart total should update
7. ✅ Cart badge should update
8. ✅ Click "-" button
9. ✅ Quantity should decrease by 1

**Expected**: Quantity updates reflected in price calculations

---

### 6. Remove Item Test
**Goal**: Verify item removal works

**Steps**:
1. ✅ On cart page with items
2. ✅ Click "Remove" button on any item
3. ✅ Should see confirmation: "Are you sure you want to remove this item?"
4. ✅ Click "OK"
5. ✅ Page should reload
6. ✅ Item should be gone
7. ✅ Cart total should update
8. ✅ Cart badge should update

**Expected**: Item removed from cart, totals updated

---

### 7. Clear Cart Test
**Goal**: Verify clearing entire cart works

**Steps**:
1. ✅ On cart page with items
2. ✅ Click "Clear Cart" button (red button)
3. ✅ Should see confirmation: "Are you sure you want to clear your entire cart?"
4. ✅ Click "OK"
5. ✅ Page should reload
6. ✅ Should see empty cart state:
   - Large cart icon
   - "Your Cart is Empty" message
   - "Browse Books" button
7. ✅ Cart badge should show "0" or hide

**Expected**: All items removed, empty state displayed

---

### 8. Empty Cart State Test
**Goal**: Verify empty cart displays correctly

**Steps**:
1. ✅ Clear cart (from Test 7)
2. ✅ Or go to `/cart` with no items
3. ✅ Should see:
   - Empty cart icon
   - "Your Cart is Empty" heading
   - Descriptive message
   - "Browse Books" button
4. ✅ Click "Browse Books"
5. ✅ Should navigate to books page

**Expected**: Friendly empty state encourages browsing

---

### 9. Cart Persistence Test
**Goal**: Verify cart persists across sessions

**Steps**:
1. ✅ Add books to cart
2. ✅ Note the cart count
3. ✅ Log out
4. ✅ Close browser completely
5. ✅ Reopen browser
6. ✅ Go to site and log in
7. ✅ Check cart badge
8. ✅ Visit cart page

**Expected**: Cart items still there after re-login

---

### 10. Book Detail Page Test
**Goal**: Verify "Add to Cart" works on detail page

**Steps**:
1. ✅ Log in
2. ✅ Go to Books page
3. ✅ Search for a book
4. ✅ Click "Details" on any book
5. ✅ Should see book detail page
6. ✅ Should see "Add to Cart" button (if logged in)
7. ✅ Click "Add to Cart"
8. ✅ Should see success toast
9. ✅ Cart badge should update

**Expected**: Can add to cart from detail page

---

### 11. Toast Notification Test
**Goal**: Verify all notification types work

**Steps**:
1. ✅ Add book to cart → Should see green success toast
2. ✅ Try to add to cart when not logged in → Should see red error toast
3. ✅ Remove item from cart → Should see confirmation dialog
4. ✅ Notifications should:
   - Slide in from right
   - Have appropriate icon
   - Auto-dismiss after 3 seconds
   - Be readable on mobile

**Expected**: Notifications provide clear feedback

---

### 12. Dashboard Cart Count Test
**Goal**: Verify dashboard shows cart count

**Steps**:
1. ✅ Log in
2. ✅ Add books to cart (e.g., 3 books)
3. ✅ Go to Dashboard
4. ✅ Look at "Cart Items" stat card
5. ✅ Should show "3" (or actual count)
6. ✅ Add another book
7. ✅ Refresh dashboard
8. ✅ Count should update to 4

**Expected**: Dashboard reflects current cart count

---

### 13. Mobile Responsiveness Test
**Goal**: Verify cart works on mobile

**Steps**:
1. ✅ Open browser DevTools (F12)
2. ✅ Toggle device toolbar (Ctrl+Shift+M)
3. ✅ Select "iPhone 12 Pro" or similar
4. ✅ Test cart page layout:
   - Items stack vertically
   - Buttons are touch-friendly
   - Text is readable
   - Summary moves below items
5. ✅ Test toast notifications (should fit screen)
6. ✅ Test "Add to Cart" buttons on books page

**Expected**: Fully functional on mobile devices

---

### 14. Error Handling Test
**Goal**: Verify graceful error handling

**Scenarios to Test**:

**A. No Internet (simulated)**:
1. ✅ Open DevTools → Network tab
2. ✅ Set to "Offline"
3. ✅ Try to add to cart
4. ✅ Should see error toast

**B. Invalid Book**:
1. ✅ Try to add book that doesn't exist (hard to test without direct API call)
2. ✅ Should see error message

**C. Server Error**:
1. ✅ Stop Flask server
2. ✅ Try to add to cart
3. ✅ Should see error toast or connection error

**Expected**: Errors handled gracefully with user feedback

---

### 15. Checkout Button Test
**Goal**: Verify checkout button shows placeholder

**Steps**:
1. ✅ Add items to cart
2. ✅ Go to cart page
3. ✅ Click "Proceed to Checkout" button
4. ✅ Should see alert: "Checkout functionality will be implemented in Phase 6!"

**Expected**: Placeholder works, ready for Phase 6

---

## 🐛 Bug Report Template

If you find issues, use this template:

```markdown
### Bug: [Short description]

**Steps to Reproduce**:
1. 
2. 
3. 

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happened]

**Browser**: [Chrome/Firefox/Safari]
**Screenshot**: [If applicable]
**Console Errors**: [Check browser console, F12]
```

---

## ✅ Testing Checklist Summary

- [ ] Test 1: Cart Badge Test
- [ ] Test 2: Add to Cart (Not Logged In)
- [ ] Test 3: Add to Cart (Logged In)
- [ ] Test 4: View Cart
- [ ] Test 5: Update Quantity
- [ ] Test 6: Remove Item
- [ ] Test 7: Clear Cart
- [ ] Test 8: Empty Cart State
- [ ] Test 9: Cart Persistence
- [ ] Test 10: Book Detail Page
- [ ] Test 11: Toast Notifications
- [ ] Test 12: Dashboard Cart Count
- [ ] Test 13: Mobile Responsiveness
- [ ] Test 14: Error Handling
- [ ] Test 15: Checkout Button

---

## 🎯 Priority Tests

**Must Test** (Critical functionality):
1. ✅ Test 3: Add to Cart (Logged In)
2. ✅ Test 4: View Cart
3. ✅ Test 5: Update Quantity
4. ✅ Test 6: Remove Item

**Should Test** (Important but not critical):
5. ✅ Test 2: Add to Cart (Not Logged In)
6. ✅ Test 7: Clear Cart
7. ✅ Test 9: Cart Persistence

**Nice to Test** (Quality of life):
8. ✅ Test 1: Cart Badge
9. ✅ Test 11: Toast Notifications
10. ✅ Test 13: Mobile Responsiveness

---

## 🚨 Known Issues

**Expected Issues** (not bugs):
1. Books default to $9.99 (no real pricing data)
2. Book images are placeholders
3. Promo code section doesn't work (Phase 6)
4. Checkout button shows alert (Phase 6)
5. Dashboard cart count needs page refresh

**Jinja2 Lint Warnings**:
- Harmless template syntax warnings in books.html and book_detail.html
- Will not affect functionality

---

## 📊 Testing Report Template

After testing, fill out:

```markdown
## Testing Report - Phase 5 Shopping Cart

**Date**: [Date]
**Tester**: [Your name]
**Browser**: [Browser and version]

### Test Results
- Tests Passed: __/15
- Tests Failed: __/15
- Critical Bugs Found: __

### Critical Issues
[List any critical bugs]

### Minor Issues
[List any minor bugs]

### Suggestions
[Any improvement suggestions]

### Overall Assessment
[Pass/Fail/Partial]
```

---

## 🎉 Happy Testing!

The shopping cart is ready to use. Enjoy exploring the new functionality!

**Next**: After testing, we can move to Phase 6 for checkout and payment integration.

---

**Created**: October 2, 2025  
**Last Updated**: October 2, 2025
