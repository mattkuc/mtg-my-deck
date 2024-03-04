// autocomplete.js

$(document).ready(function () {
    // Get the list of card names
    var card_name = card_name; // Replace 'cardNames' with the actual data from your Flask app

    // Initialize the autocomplete functionality
    $("#card_name").autocomplete({
        source: function (request, response) {
            var term = request.term.toLowerCase();
            var filteredNames = $.grep(card_name, function (value) {
                return value.toLowerCase().indexOf(term) >= 0;
            });
            response(filteredNames);
        },
        minLength: 2, // Set the minimum length before autocomplete starts
        select: function (event, ui) {
            // Make an AJAX request to your Flask route
            $.ajax({
                type: 'POST',
                url: '/get_card_data',
                data: { selected_card_name: ui.item.value },
                success: function (data) {
                    console.log('Card data received:', data);
                    // You can further process the data here, e.g., display it on the page

                    // Reload the page after receiving the data
                    location.reload();
                },
                error: function (error) {
                    console.error('Error:', error);
                }
            });
        }
    });
});
