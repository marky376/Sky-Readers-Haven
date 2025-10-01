/**
 * Toggles the menu icon and opens/closes the navbar when the menu icon is clicked.
 * @param {Event} event - The click event.
 */
let menu = document.querySelector('#menu-icon');
let navbar = document.querySelector('.navmenu');

menu.onclick = (event) => {
    menu.classList.toggle('bx-x');
    navbar.classList.toggle('open');
}

/**
 * Handles the click event of the app button.
 * Prevents the default behavior, displays an alert, and opens a new window/tab with the button's href.
 * @param {Event} event - The click event.
 */
document.addEventListener("DOMContentLoaded", function() {
    const appButton = document.querySelector('.button');
    appButton.addEventListener('click', function(event) {
        event.preventDefault();
        alert('Button clicked');
        window.open(this.href, '_blank');
    });
});
