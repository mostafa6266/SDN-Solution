const myButton = document.getElementById('myButton');
im
// Add event listener to the button
myButton.addEventListener('click', function login() {
    // Redirect to another page
    window.location.href = "home.html ";
});
var backgroundImageArray = [
"static\images/po.jpg",
"static\images//1398865.jpg",
"static\images/im4.jpg"
];

function changeBackgroundImage() {
    var randomIndex = Math.floor(Math.random() * backgroundImageArray.length);
    var selectedImage = backgroundImageArray[randomIndex];
    document.body.style.backgroundImage = 'url(' + selectedImage + ')';
}

// Change the background when the page loads
window.onload = changeBackgroundImage;
