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
LAST_CATEGORY_FILE = "last_category.json"  # Stores last used category for cycling

# Hugging Face API for Question Generation
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
HUGGINGFACE_HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

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

# Midnight Club Characters
MIDNIGHT_CLUB_CHARACTERS = [
    "Oscar", "Angel", "Apone", "Moses", "Savo", "Tomoya", "Vince", "Dice", "Gina", "Vito", "Andrew", "Phil",
    "Vanessa", "Brooke", "Lamont", "Carlos", "Bishop", "Kioshi", "Caesar", "Angel", "Leo", 
    "Trust Fund Baby From MC2", "Hector", "The City Champs", "Andrew", "Roy", "Annie",
    "Fernando", "Karol", "Doc", "Baby-T", "Yo-Yo", "Nails", "Arnie", "Rachel", "Sara", "Kayla", "Walker", 
    "AJ", "Lester"
]

# Function to Get a Funny LGBTQ+ Themed Question
def generate_funny_question():
    data = {"inputs": "Give me a funny LGBTQ+ question for a game"}
    response = requests.post(HUGGINGFACE_API_URL, headers=HUGGINGFACE_HEADERS, json=data)
    
    try:
        result = response.json()
        return result[0]["generated_text"]
    except:
        # Fallback if API fails
        return random.choice([
            "What’s the most sus thing you can say about `{}`?",
            "Describe `{}` in the gayest way possible.",
            "How would `{}` fit into Midnight Club if it was a car mod?",
            "If `{}` was a character in Midnight Club, what would their backstory be?",
            "Speedrun `{}`. What’s the fastest way to make it sound dirty?",
        ])

# Function to Fetch a Random Car
def get_random_car():
    return random.choice(MIDNIGHT_CLUB_CARS)

# Function to Fetch a Random Midnight Club Character
def get_random_mc_character():
    return random.choice(MIDNIGHT_CLUB_CHARACTERS)

# Function to Fetch a Random Gaming Character
def get_random_game_character():
    try:
        headers = {"User-Agent": "GayChallengeBot"}
        response = requests.get(f"https://www.giantbomb.com/api/characters/?api_key={GIANT_BOMB_API_KEY}&format=json", headers=headers)
        data = response.json()
        character_list = data["results"]
        return random.choice(character_list)["name"]
    except:
        return "Captain Falcon"  # Fallback character

# Function to Determine Next Category in Cycle
def get_next_category():
    categories = ["car", "mc_character", "game_character"]

    if not os.path.exists(LAST_CATEGORY_FILE):
        last_category = None
    else:
        with open(LAST_CATEGORY_FILE, "r") as f:
            last_category = json.load(f).get("last_category")

    # Determine next category
    if last_category not in categories:
        next_category = categories[0]  # Start from the first category if no valid history
    else:
        current_index = categories.index(last_category)
        next_category = categories[(current_index + 1) % len(categories)]  # Cycle to next

    # Save new category
    with open(LAST_CATEGORY_FILE, "w") as f:
        json.dump({"last_category": next_category}, f)

    return next_category

# Function to Generate Full Challenge
def generate_challenge():
    category = get_next_category()

    if category == "car":
        subject = get_random_car()
    elif category == "mc_character":
        subject = get_random_mc_character()
    else:
        subject = get_random_game_character()

    question_template = generate_funny_question()
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

    # Send to Test Webhook (webhook.site)
    test_response = requests.post(TEST_WEBHOOK_URL, json=data)
    if test_response.status_code == 204:
        print("✅ Test challenge sent successfully to Webhook.site!")
    else:
        print(f"❌ Failed to send test message. Status Code: {test_response.status_code} - {test_response.text}")

    return response.json() if response.status_code == 200 else None

# Function to Pin Message in Discord
def pin_message(message_id):
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/pins/{message_id}"
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.put(url, headers=headers)
    
    if response.status_code == 204:
        print("📌 Message pinned successfully!")
    else:
        print(f"❌ Failed to pin message. Status Code: {response.status_code} - {response.text}")

# Execute the Workflow
message_response = send_challenge()

# If message was sent, extract ID and pin it
if message_response and "id" in message_response:
    message_id = message_response["id"]
    pin_message(message_id)
else:
    print("⚠️ Message ID not found. Unable to pin.")
