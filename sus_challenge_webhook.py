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
GIANTBOMB_API_KEY = os.getenv("GIANTBOMB_API_KEY")  # Giant Bomb API Key

# Hugging Face API for Better Text Generation
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/gpt2"  # Change to "bloom" if needed
HUGGINGFACE_HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# Giant Bomb API for Game Characters
GAMING_CHARACTER_API = f"https://www.giantbomb.com/api/characters/?api_key={GIANTBOMB_API_KEY}&format=json"

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

# Rotating between categories
ROTATION_INDEX = 0
CATEGORY_LIST = ["car", "midnight_character", "game_character"]

# Function to fetch a random car
def get_random_car():
    return random.choice(MIDNIGHT_CLUB_CARS)

# Function to fetch a random Midnight Club character
def get_random_midnight_character():
    return random.choice(MIDNIGHT_CLUB_CHARACTERS)

# Function to fetch a random gaming character from Giant Bomb API
def get_random_game_character():
    try:
        headers = {"User-Agent": "GayChallengeBot"}
        response = requests.get(GAMING_CHARACTER_API, headers=headers)
        data = response.json()

        if "results" in data and data["results"]:
            return random.choice(data["results"])["name"]
        else:
            raise ValueError("No results from Giant Bomb API.")

    except Exception as e:
        print(f"❌ Giant Bomb API Error: {e}")  # Log error
        return random.choice(MIDNIGHT_CLUB_CHARACTERS)  # Fallback

# Function to rotate between categories
def get_random_subject():
    global ROTATION_INDEX
    category = CATEGORY_LIST[ROTATION_INDEX]
    
    if category == "car":
        subject = get_random_car()
    elif category == "midnight_character":
        subject = get_random_midnight_character()
    else:
        subject = get_random_game_character()

    # Move to the next category
    ROTATION_INDEX = (ROTATION_INDEX + 1) % len(CATEGORY_LIST)
    return subject, category

# Function to generate a funny LGBTQ+ question
def generate_funny_question(subject, category):
    try:
        prompt = f"Generate a funny LGBTQ+ question about a {category}: {subject}."
        data = {"inputs": prompt}
        response = requests.post(HUGGINGFACE_API_URL, headers=HUGGINGFACE_HEADERS, json=data)
        result = response.json()

        print(f"🔍 Hugging Face API Response: {result}")  # Debugging Log

        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        else:
            raise ValueError("No valid text returned from API.")

    except Exception as e:
        print(f"❌ Hugging Face API Error: {e}")  # Log error
        print("⚠️ Falling back to default question templates.")

        # Ensure the question fits the category
        if category == "car":
            return random.choice([
                "How would `{}` be modified in the gayest way possible?",
                "What if `{}` had a fabulous pride-themed paint job?",
                "If `{}` could talk, what super gay thing would it say?",
            ]).format(subject)
        elif category == "midnight_character":
            return random.choice([
                "Describe `{}` in the gayest way possible.",
                "If `{}` was in a pride parade, what would they wear?",
                "Speedrun `{}`. What’s the fastest way to make it sound dirty?",
            ]).format(subject)
        else:  # game_character
            return random.choice([
                "What if `{}` was a drag queen, what would their stage name be?",
                "Describe `{}` as if they were the lead in a gay romance movie.",
                "If `{}` had to survive using only sass, how would they win?",
            ]).format(subject)

# Function to generate the challenge message
def generate_challenge():
    subject, category = get_random_subject()
    question = generate_funny_question(subject, category)
    return question

# Function to send the challenge to Discord Webhook
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

# Function to pin message in Discord
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

# Execute the workflow
message_response = send_challenge()

# If message was sent, extract ID and pin it
if message_response and "id" in message_response:
    message_id = message_response["id"]
    pin_message(message_id)
else:
    print("⚠️ Message ID not found. Unable to pin.")
