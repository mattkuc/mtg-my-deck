
def get_card_names_from_file():
    with open('card_names.txt', 'r') as file:
        card_names = [line.strip() for line in file.readlines()]
    return card_names



def get_matching_card_names(prefix):
    # Example function that returns matching card names
    # Replace this with your actual logic to fetch matching names
    card_names = get_card_names_from_file()
    matching_names = [name for name in card_names if name.lower().startswith(prefix.lower())]
    return matching_names
