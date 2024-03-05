// static/autocomplete.js

$(document).ready(function() {
    var cardNameInput = $('#card_name');
    var ghostText = $('#ghost-text');

    cardNameInput.on('input', function() {
        var inputVal = $(this).val();
        $.get('/autocomplete', { prefix: inputVal }, function(data) {
            if (data.length > 0) {
                // Show the suggestion as ghost text
                var suggestion = data[0].substring(inputVal.length);
                showGhostText(suggestion);
            } else {
                // Hide the ghost text if no suggestions
                hideGhostText();
            }
        });
    });

    // Handle keydown events
    cardNameInput.on('keydown', function(event) {
        if (event.key === 'Tab') {
            event.preventDefault();
            var suggestion = ghostText.text();
            if (suggestion) {
                fillRestOfText(suggestion);
            }
        }
    });

    // Function to show the suggestion as ghost text
    function showGhostText(suggestion) {
        ghostText.text(suggestion);
    }

    // Function to hide the ghost text
    function hideGhostText() {
        ghostText.text('');
    }

    // Function to fill the rest of the text with the suggestion
    function fillRestOfText(suggestion) {
        cardNameInput.val(cardNameInput.val() + suggestion);
        hideGhostText();
    }
});
