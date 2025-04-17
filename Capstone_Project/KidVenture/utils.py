import random

def generate_random_username():
    adjectives = ["Swift", "Brave", "Quiet", "Witty", "Fuzzy", "Bold"]
    animals = ["Fox", "Lion", "Koala", "Otter", "Panda", "Eagle"]

    adjective = random.choice(adjectives)
    animal = random.choice(animals)
    number = random.randint(100, 999)

    return f"{adjective}{animal}{number}"