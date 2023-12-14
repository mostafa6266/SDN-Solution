// Add an active class to the clicked navigation item
const navItems = document.querySelectorAll('nav ul li a');

navItems.forEach(item => {
    item.addEventListener('click', function() {
        navItems.forEach(navItem => {
            navItem.classList.remove('active');
        });
        this.classList.add('active');
    });
});