import requests
import random
import json
import os
from datetime import datetime, timedelta

# Your Webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1342757700479483984/DZnOYPMzrb3tkMN_T1XMSvoOFWC5HlIJv3mwtC-ykhoNSu-drCCaVw08qL388YGg30fh"

### API Endpoints ###
CAR_API = "https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json"
SPORTS_API = "https://www.thesportsdb.com/api/v1/json/1/all_teams.php?s=Soccer"
URBAN_DICTIONARY_API = "https://api.urbandictionary.com/v0/random"

# JSON file for tracking past selections
TRACKING_FILE = "selection_history.json"

# Midnight Club Vehicles (Expanded)
MIDNIGHT_CLUB_CARS = [
    "Big Red DUB Escalade", "Black DUB EXT", "DUB Chrysler 300C", "DUB Dodge Magnum",
    "DUB Mercedes-Benz SL55 AMG", "68 Pontiac GTO", "DUB 96 Chevy Impala SS", "Hummer H1",
    "Lamborghini Murciélago", "Nissan Skyline GT-R R34", "Toyota Supra MK4",
    "69 Pymouth Netcoder", " 2005 Ford Mustang GT", "Pagani Zonda C12", "81 Chevrolet Camaro Z28",
    "Mitsubishi 3000GT VR-4", "Saleen S7 Twin Turbo", "Audi RS4", "DUB Dodge Charger SRT8",
    "Chrysler ME Four Twelve", "Volkswagen Golf R32", "Mitsubishi Lancer Evo VIII", "Saiku XS", "Bryston V",
  "Scneller V8", "Cocotte", "Veloci", "Emu", "71 Bestia", "Smugglers Run Buggie", "SLF"
]

# Midnight Club Named Characters
MIDNIGHT_CLUB_CHARACTERS = [
    "Oscar", "Angel", "Apone" , "Moses", "Savo", "Tomoya", "Vince" , "Dice", "Gina", "Vito", "Andrew", "Phil",
    "Vanessa", "Booke", "Lamont", "Carlos", "Bishop", "Kioshi", "Caesar", "Angel", "Leo", "Trust Fund Baby From MC2", "Hector"
    "The City Champs", "Andrew", "Roy", "Annie",
    "Fernando", "Karol", "Doc", "Baby-T", "Yo-Yo", "Nails", "Arnie", "Rachel", "Sara", "Kayla", "Walker", "AJ", "Lester", 
]

# General Sus Question Templates
QUESTION_TEMPLATES = [
    "What’s the most sus thing you can say about `{}`?",
    "Describe `{}` in the gayest way possible.",
    "How would `{}` fit into Midnight Club if it was a car mod?",
    "If `{}` was a character in Midnight Club, what would their backstory be?",
    "Speedrun `{}`. What’s the fastest way to make it sound dirty?",
]

# Function to load past selections
def load_selection_history():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, "r") as f:
            return json.load(f)
    return {"cars": {}, "characters": {}}

# Function to save selection history
def save_selection_history(history):
    with open(TRACKING_FILE, "w") as f:
        json.dump(history, f, indent=4)

# Function to get a unique selection
def get_unique_selection(category_list, category_key):
    history = load_selection_history()
    used_items = history.get(category_key, {})

    # Filter out items used in the last 30 days
    valid_items = [
        item for item in category_list if item not in used_items or
        datetime.strptime(used_items[item], "%Y-%m-%d") < datetime.now() - timedelta(days=30)
    ]

    # If all items have been used, reset history
    if not valid_items:
        valid_items = category_list
        history[category_key] = {}

    selected_item = random.choice(valid_items)

    # Save selection with today's date
    history[category_key][selected_item] = datetime.now().strftime("%Y-%m-%d")
    save_selection_history(history)

    return selected_item

# Function to fetch a random car from API
def get_random_car():
    try:
        response = requests.get(CAR_API)
        data = response.json()
        car_list = data["Results"]
        return random.choice(car_list)["Make_Name"]
    except:
        return get_unique_selection(MIDNIGHT_CLUB_CARS, "cars")  # Fallback

# Function to fetch a random sports team
def get_random_team():
    try:
        response = requests.get(SPORTS_API)
        data = response.json()
        teams = data["teams"]
        return random.choice(teams)["strTeam"]
    except:
        return "FC Midnight"

# Function to fetch a random Urban Dictionary word
def get_random_slang():
    try:
        response = requests.get(URBAN_DICTIONARY_API)
        data = response.json()
        return random.choice(data["list"])["word"]
    except:
        return "Turbo Thrust"  # Fallback word

# Function to generate a random challenge
def generate_challenge():
    options = [
        get_random_car(),
        get_random_team(),
        get_random_slang(),
        get_unique_selection(MIDNIGHT_CLUB_CHARACTERS, "characters"),
    ]
    random_item = random.choice(options)
    return random.choice(QUESTION_TEMPLATES).format(random_item)

# Create the message
challenge = generate_challenge()
data = {
    "content": f"🌈 **Gayest Comment Challenge!** 🌈\n💬 {challenge}\n\n🗳️ **Vote for the best response!** React with 🔥 or 💀.",
    "username": "Gay Police",
}

# Send to Discord Webhook
response = requests.post(WEBHOOK_URL, json=data)

if response.status_code == 204:
    print("✅ Challenge sent successfully!")
else:
    print(f"❌ Failed to send. Status Code: {response.status_code}")
