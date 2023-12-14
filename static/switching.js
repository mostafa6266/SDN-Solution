// Get references to the input elements
const inputText = document.getElementById('inputText');
const addButton = document.getElementById('addButton');
const container = document.getElementById('container');

// Add event listener to the add button
addButton.addEventListener('click', function() {
    // Get the entered information
    const info = inputText.value;

    // Create a new div element
    const newDiv = document.createElement('div');
    newDiv.classList.add('dynamicDiv');
    newDiv.textContent = info;

    // Append the new div to the container
    container.appendChild(newDiv);

    // Clear the input field
    inputText.value = '';
});