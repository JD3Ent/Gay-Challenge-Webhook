import requests
import random
import json
import os
from datetime import datetime, timedelta

# Load API Keys & Webhooks from GitHub Secrets
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Discord Webhook
TEST_WEBHOOK_URL = os.getenv("TEST_WEBHOOK_URL")  # Webhook.site URL for testing
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Bot token for pinning
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")  # Discord Channel ID
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # Hugging Face API Key
GIANT_BOMB_API_KEY = os.getenv("GIANT_BOMB_API_KEY")  # Giant Bomb API Key

# API Endpoints
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
HUGGINGFACE_HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
GIANT_BOMB_API_URL = f"https://www.giantbomb.com/api/characters/?api_key={GIANT_BOMB_API_KEY}&format=json"

# Track last used category for cycling
SELECTION_TRACKER_FILE = "last_category_used.json"

# Midnight Club Vehicles (Expanded)
MIDNIGHT_CLUB_CARS = [
    "Big Red DUB Escalade", "Black DUB EXT", "DUB Chrysler 300C", "DUB Dodge Magnum",
    "DUB Mercedes-Benz SL55 AMG", "68 Pontiac GTO", "DUB 96 Chevy Impala SS", "Hummer H1",
    "Lamborghini Murciélago", "Nissan Skyline GT-R R34", "Toyota Supra MK4",
    "69 Plymouth Netcoder", "2005 Ford Mustang GT", "Pagani Zonda C12", "81 Chevrolet Camaro Z28",
    "Mitsubishi 3000GT VR-4", "Saleen S7 Twin Turbo", "Audi RS4", "DUB Dodge Charger SRT8",
    "Chrysler ME Four Twelve", "Volkswagen Golf R32", "Mitsubishi Lancer Evo VIII", "Saiku XS", 
    "Bryston V", "Scneller V8", "Cocotte", "Veloci", "Emu", "71 Bestia", "Smugglers Run Buggie", "SLF"
]

# Midnight Club Characters
MIDNIGHT_CLUB_CHARACTERS = [
    "Oscar", "Angel", "Apone", "Moses", "Savo", "Tomoya", "Vince", "Dice", "Gina", "Vito", "Andrew", "Phil",
    "Vanessa", "Brooke", "Lamont", "Carlos", "Bishop", "Kioshi", "Caesar", "Angel", "Leo", 
    "Trust Fund Baby From MC2", "Hector", "The City Champs", "Andrew", "Roy", "Annie",
    "Fernando", "Karol", "Doc", "Baby-T", "Yo-Yo", "Nails", "Arnie", "Rachel", "Sara", "Kayla", "Walker", 
    "AJ", "Lester"
]

# Context-Based Question Templates
CAR_QUESTIONS = [
    "If `{}` was a person, what kind of driver would they be?",
    "Would `{}` be a top or bottom in a Midnight Club race?",
    "Describe `{}` in the most sus way possible.",
    "If `{}` was your partner in crime, how would they help you escape the cops?",
]

CHARACTER_QUESTIONS = [
    "If `{}` had to seduce someone to win a race, how would they do it?",
    "Describe `{}`'s most sus moment in their Midnight Club career.",
    "If `{}` had a secret lover in Midnight Club, who would it be?",
    "How would `{}` flirt their way out of getting pulled over?",
]

# Function to Cycle Between Categories
def get_next_category():
    categories = ["car", "character", "game_character"]
    
    # Load last used category
    if os.path.exists(SELECTION_TRACKER_FILE):
        with open(SELECTION_TRACKER_FILE, "r") as f:
            last_category = json.load(f).get("last_used", "")
    else:
        last_category = ""

    # Determine next category
    if last_category not in categories:
        next_category = categories[0]  # Default start with cars
    else:
        current_index = categories.index(last_category)
        next_category = categories[(current_index + 1) % len(categories)]

    # Save new category selection
    with open(SELECTION_TRACKER_FILE, "w") as f:
        json.dump({"last_used": next_category}, f)

    return next_category

# Function to Get a Random Subject Based on Cycling Category
def get_random_subject():
    category = get_next_category()

    if category == "car":
        return random.choice(MIDNIGHT_CLUB_CARS), "car"
    elif category == "character":
        return random.choice(MIDNIGHT_CLUB_CHARACTERS), "character"
    else:
        return get_random_game_character(), "character"

# Function to Fetch a Random Gaming Character
def get_random_game_character():
    try:
        response = requests.get(GIANT_BOMB_API_URL)
        data = response.json()
        character_list = data["results"]
        return random.choice(character_list)["name"]
    except:
        return random.choice(MIDNIGHT_CLUB_CHARACTERS)  # Fallback

# Function to Get a Funny LGBTQ+ Themed Question
def generate_funny_question(category):
    data = {"inputs": "Generate a funny LGBTQ+ question about cars and racing" if category == "car" else "Generate a funny LGBTQ+ question about characters in a game"}
    
    response = requests.post(HUGGINGFACE_API_URL, headers=HUGGINGFACE_HEADERS, json=data)
    
    try:
        result = response.json()
        return result[0]["generated_text"]
    except:
        return random.choice(CAR_QUESTIONS if category == "car" else CHARACTER_QUESTIONS)

# Function to Generate Full Challenge
def generate_challenge():
    subject, category = get_random_subject()
    question_template = generate_funny_question(category)
    return question_template.format(subject)

# Function to Send Challenge to Webhook
def send_challenge():
    challenge = generate_challenge()
    data = {
        "content": f"🌈 **Gayest Comment Challenge!** 🌈\n💬 {challenge}\n\n🗳️ **Vote for the best response!** React with 🔥 or 💀.",
        "username": "Gay Challenge Bot"
    }

    # Send to Discord Webhook
    response = requests.post(WEBHOOK_URL, json=data)

    if response.status_code == 204:
        print("✅ Challenge sent successfully to Discord!")
    else:
        print(f"❌ Failed to send. Status Code: {response.status_code} - {response.text}")

    return response.json() if response.status_code == 200 else None

# Execute the Workflow
message_response = send_challenge()
