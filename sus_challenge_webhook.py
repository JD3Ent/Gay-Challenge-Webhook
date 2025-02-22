import requests
import random
import json
import os
from datetime import datetime, timedelta

# Webhook URLs
DISCORD_WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Discord Webhook from GitHub Secrets
TEST_WEBHOOK_URL = "https://webhook.site/72442d34-5fed-4e69-ba6a-0f92233568c5"  # For debugging

# API Endpoints
CAR_API = "https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json"
SPORTS_API = "https://www.thesportsdb.com/api/v1/json/1/all_teams.php?s=Soccer"
GAMING_CHARACTER_API = "https://www.giantbomb.com/api/characters/?api_key=YOUR_GIANTBOMB_API_KEY&format=json"

# JSON file for tracking past selections
TRACKING_FILE = "selection_history.json"

# Midnight Club Vehicles
MIDNIGHT_CLUB_CARS = [
    "Big Red DUB Escalade", "Black DUB EXT", "DUB Chrysler 300C", "DUB Dodge Magnum",
    "DUB Mercedes-Benz SL55 AMG", "68 Pontiac GTO", "DUB 96 Chevy Impala SS", "Hummer H1",
    "Lamborghini Murciélago", "Nissan Skyline GT-R R34", "Toyota Supra MK4",
    "69 Plymouth Netcoder", "2005 Ford Mustang GT", "Pagani Zonda C12", "81 Chevrolet Camaro Z28",
    "Mitsubishi 3000GT VR-4", "Saleen S7 Twin Turbo", "Audi RS4", "DUB Dodge Charger SRT8",
    "Chrysler ME Four Twelve", "Volkswagen Golf R32", "Mitsubishi Lancer Evo VIII", "Saiku XS", 
    "Bryston V", "Scneller V8", "Cocotte", "Veloci", "Emu", "71 Bestia", "Smugglers Run Buggie", "SLF"
]

# Midnight Club Named Characters
MIDNIGHT_CLUB_CHARACTERS = [
    "Oscar", "Angel", "Apone", "Moses", "Savo", "Tomoya", "Vince", "Dice", "Gina", "Vito", "Andrew", "Phil",
    "Vanessa", "Brooke", "Lamont", "Carlos", "Bishop", "Kioshi", "Caesar", "Angel", "Leo", 
    "Trust Fund Baby From MC2", "Hector", "The City Champs", "Andrew", "Roy", "Annie",
    "Fernando", "Karol", "Doc", "Baby-T", "Yo-Yo", "Nails", "Arnie", "Rachel", "Sara", "Kayla", "Walker", 
    "AJ", "Lester"
]

# General Sus Question Templates
QUESTION_TEMPLATES = [
    "What’s the most sus thing you can say about `{}`?",
    "Describe `{}` in the gayest way possible.",
    "How would `{}` fit into Midnight Club if it was a car mod?",
    "If `{}` was a character in Midnight Club, what would their backstory be?",
    "Speedrun `{}`. What’s the fastest way to make it sound dirty?",
]

# Load past selections
def load_selection_history():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, "r") as f:
            return json.load(f)
    return {"cars": {}, "characters": {}}

# Save selection history
def save_selection_history(history):
    with open(TRACKING_FILE, "w") as f:
        json.dump(history, f, indent=4)

# Get a unique selection
def get_unique_selection(category_list, category_key):
    history = load_selection_history()
    used_items = history.get(category_key, {})

    valid_items = [
        item for item in category_list if item not in used_items or
        datetime.strptime(used_items[item], "%Y-%m-%d") < datetime.now() - timedelta(days=30)
    ]

    if not valid_items:
        valid_items = category_list
        history[category_key] = {}

    selected_item = random.choice(valid_items)
    history[category_key][selected_item] = datetime.now().strftime("%Y-%m-%d")
    save_selection_history(history)

    return selected_item

# Fetch a random car
def get_random_car():
    try:
        response = requests.get(CAR_API)
        data = response.json()
        car_list = data["Results"]
        return random.choice(car_list)["Make_Name"]
    except:
        return get_unique_selection(MIDNIGHT_CLUB_CARS, "cars")

# Fetch a random sports team
def get_random_team():
    try:
        response = requests.get(SPORTS_API)
        data = response.json()
        teams = data["teams"]
        return random.choice(teams)["strTeam"]
    except:
        return "FC Midnight"

# Fetch a random gaming character
def get_random_game_character():
    try:
        headers = {"User-Agent": "GayChallengeBot"}
        response = requests.get(GAMING_CHARACTER_API, headers=headers)
        data = response.json()
        character_list = data["results"]
        return random.choice(character_list)["name"]
    except:
        return get_unique_selection(MIDNIGHT_CLUB_CHARACTERS, "characters")

# Generate a challenge
def generate_challenge():
    options = [
        get_random_car(),
        get_random_team(),
        get_random_game_character(),
        get_unique_selection(MIDNIGHT_CLUB_CHARACTERS, "characters"),
    ]
    random_item = random.choice(options)
    return random.choice(QUESTION_TEMPLATES).format(random_item)

# Create the message
challenge = generate_challenge()
data = {
    "content": f"🌈 **Gayest Comment Challenge!** 🌈\n💬 {challenge}\n\n🗳️ **Vote for the best response!** React with 🔥 or 💀.",
    "username": "Gay Challenge Bot"
}

# Send to Discord Webhook
if DISCORD_WEBHOOK_URL:
    discord_response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if discord_response.status_code == 204:
        print("✅ Challenge sent to Discord successfully!")
    else:
        print(f"❌ Discord Webhook failed. Status Code: {discord_response.status_code} - {discord_response.text}")

# Send test message to Webhook.site
if TEST_WEBHOOK_URL:
    test_response = requests.post("https://webhook.site/72442d34-5fed-4e69-ba6a-0f92233568c5", json=data)
    if test_response.status_code == 200:
        print("✅ Test challenge sent successfully to Webhook.site!")
    else:
        print(f"❌ Webhook.site test failed. Status Code: {test_response.status_code} - {test_response.text}")
