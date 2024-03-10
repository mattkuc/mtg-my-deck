
$(document).ready(function() {
    var cardNameInput = $('#card_name');
    var ghostText = $('#ghost-text');

    cardNameInput.on('input', function() {
        var inputVal = $(this).val();
        $.get('/autocomplete', { prefix: inputVal }, function(data) {
            if (data.length > 0) {
                var suggestion = data[0].substring(inputVal.length);
                showGhostText(suggestion);
            } else {
                hideGhostText();
            }
        });
    });

    cardNameInput.on('keydown', function(event) {
        if (event.key === 'Tab') {
            event.preventDefault();
            var suggestion = ghostText.text();
            if (suggestion) {
                fillRestOfText(suggestion);
            }
        }
    });

    function showGhostText(suggestion) {
        ghostText.text(suggestion);
    }

    function hideGhostText() {
        ghostText.text('');
    }

    function fillRestOfText(suggestion) {
        cardNameInput.val(cardNameInput.val() + suggestion);
        hideGhostText();
    }
});
