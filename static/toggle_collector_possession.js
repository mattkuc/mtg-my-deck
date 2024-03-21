function togglePossession(cardId, tableName) {
    const postData = {
        cardId: cardId,
    };

    fetch(`/update_possession/${tableName}/${cardId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(postData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const cardElement = document.getElementById(`card-${cardId}`);
            cardElement.classList.toggle('in-possession');
            cardElement.classList.toggle('not-in-possession');
        } else {
            console.error('Failed to update possession status.');
        }
    })
    .catch(error => console.error('Error:', error));
}
