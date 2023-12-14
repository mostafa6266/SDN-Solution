// // Get references to the search input and search results container
// const searchInput = document.getElementById('searchInput');
// const searchResults = document.getElementById('searchResults');

// // Add an event listener to the search input
// searchInput.addEventListener('input', function() {
//     // Clear previous search results
//     searchResults.innerHTML = '';

//     // Get the search query
//     const query = searchInput.value.toLowerCase();

//     // Perform the search
//     if (query.length > 0) {
//         // Loop through your page content and filter based on the search query
//         // For example, if you have a list of items, you can filter them like this:
//         const items = ['Item 1', 'Item 2', 'Item 3', 'Item 4'];
//         const filteredItems = items.filter(item => item.toLowerCase().includes(query));

//         // Display the search results
//         filteredItems.forEach(item => {
//             const resultItem = document.createElement('div');
//             resultItem.textContent = item;
//             searchResults.appendChild(resultItem);
//         });
//     }
// });
// search.js

document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    const searchInput = document.querySelector("#searchInput");
    const ipResultDiv = document.querySelector("#ipResultDiv");

    form.addEventListener("submit", function(event) {
        event.preventDefault();

        const mac = searchInput.value;

        // Perform an AJAX request to your Django view
        fetch("/your_django_view_url/", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        })
        .then(response => response.json())
        .then(data => {
            // Update the ipResultDiv with the result
            ipResultDiv.innerHTML = data.ip_result;
        })
        .catch(error => {
            console.error("Error:", error);
        });
    });
});
