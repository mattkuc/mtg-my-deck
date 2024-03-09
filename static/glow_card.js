document.addEventListener("DOMContentLoaded", function () {
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        const rarity = card.getAttribute('data-rarity');
        card.classList.add(getRarityClass(rarity));
        card.addEventListener('mouseenter', addGlow);
        card.addEventListener('mouseleave', removeGlow);
    });
});

function getRarityClass(rarity) {
    switch (rarity) {
        case 'mythic':
            return 'mythic-glow';
        case 'rare':
            return 'rare-glow';
        case 'uncommon':
            return 'uncommon-glow';
        case 'common':
            return 'common-no-glow';
        default:
            return '';
    }
}

function addGlow() {
    this.classList.add('glow-on-hover');
}

function removeGlow() {
    this.classList.remove('glow-on-hover');
}
