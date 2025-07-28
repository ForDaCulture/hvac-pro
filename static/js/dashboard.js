// This file can be used for any site-wide JavaScript.
// For now, it's a placeholder.
console.log("HVAC Pro dashboard script loaded.");

// Example: Add smooth scrolling for any anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});
