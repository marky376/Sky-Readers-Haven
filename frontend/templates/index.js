let menu = document.querySelector('#menu-icon');
let navbar = document.querySelector('.navmenu');

menu.onclick = () => {
    menu.classList.toggle('bx-x');
    navbar.classList.toggle('open');
}

document.addEventListener("DOMContentLoaded", function() {
    const appButton = document.querySelector('.button');
    appButton.addEventListener('click', function() {
        event.preventDefault();
        alert('Button clicked');
        window.open(this.href, '_blank');
    });
});
