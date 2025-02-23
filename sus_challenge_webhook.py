import requests
import random
import os
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Discord Webhook
TEST_WEBHOOK_URL = os.getenv("TEST_WEBHOOK_URL")  # Webhook.site URL for testing
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Bot token for pinning
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")  # Discord Channel ID
GIANTBOMB_API_KEY = os.getenv("GIANTBOMB_API_KEY")  # Giant Bomb API Key

# Giant Bomb API Config
GAMING_CHARACTER_API = f"https://www.giantbomb.com/api/characters/?api_key={GIANTBOMB_API_KEY}&format=json"

# Midnight Club Vehicles
MIDNIGHT_CLUB_CARS = [
    "Big Red DUB Escalade", "Black DUB EXT", "DUB Chrysler 300C", "DUB Dodge Magnum",
    "DUB Mercedes-Benz SL55 AMG", "68 Pontiac GTO", "DUB 96 Chevy Impala SS", "Hummer H1",
    "Lamborghini Murciélago", "Nissan Skyline GT-R R34", "Toyota Supra MK4",
    "69 Plymouth Netcoder", "2005 Ford Mustang GT", "Pagani Zonda C12", "81 Chevrolet Camaro Z28",
    "Mitsubishi 3000GT VR-4", "Saleen S7 Twin Turbo", "Audi RS4", "DUB Dodge Charger SRT8",
    "Chrysler ME Four Twelve", "Volkswagen Golf R32", "Mitsubishi Lancer Evo VIII", "Saiku XS",
    "Bryston V", "Scneller V8", "Cocotte", "Veloci", "Emu", "71 Bestia",
    "Smugglers Run Buggie", "SLF"
]

# Midnight Club Characters
MIDNIGHT_CLUB_CHARACTERS = [
    "Oscar", "Angel", "Apone", "Moses", "Savo", "Tomoya", "Vince", "Dice", "Gina", "Vito", "Andrew", "Phil",
    "Vanessa", "Brooke", "Lamont", "Carlos", "Bishop", "Kioshi", "Caesar", "Angel", "Leo", 
    "Trust Fund Baby From MC2", "Hector", "The City Champs", "Andrew", "Roy", "Annie",
    "Fernando", "Karol", "Doc", "Baby-T", "Yo-Yo", "Nails", "Arnie", "Rachel", "Sara", "Kayla", "Walker", 
    "AJ", "Lester"

]

CATEGORY_LIST = ["car", "midnight_character", "game_character"]

# Load questions from an external file
def load_questions(file_path):
    try:
        with open(file_path, 'r') as f:
            questions = [line.strip() for line in f if line.strip()]
            logging.info(f"Loaded {len(questions)} questions from {file_path}")
            return questions
    except Exception as e:
        logging.error(f"Error loading questions from {file_path}: {e}")
        return []

# Load all predefined questions at startup
PREDEFINED_QUESTIONS = load_questions("questions.txt")
CROSSOVER_QUESTIONS = load_questions("crossover.txt")

ROTATION_INDEX = 0  # Used to rotate categories

# Function to fetch a random car
def get_random_car():
    return random.choice(MIDNIGHT_CLUB_CARS)

# Function to fetch a random Midnight Club character
def get_random_midnight_character():
    return random.choice(MIDNIGHT_CLUB_CHARACTERS)

# Function to fetch a random gaming character from Giant Bomb API
def get_random_game_character():
    try:
        headers = {"User-Agent": "SusChallengeBot"}
        response = requests.get(GAMING_CHARACTER_API, headers=headers)
        data = response.json()

        if data.get("results"):
            return random.choice(data["results"])["name"]
        else:
            raise ValueError("No results from Giant Bomb API.")
    
    except Exception as e:
        logging.error(f"Giant Bomb API Error: {e}")
        return random.choice(MIDNIGHT_CLUB_CHARACTERS)  # Fallback

# Function to rotate between categories (preserves rotation logic)
def get_random_subject():
    global ROTATION_INDEX
    category = CATEGORY_LIST[ROTATION_INDEX]
    
    if category == "car":
        subject = get_random_car()
    elif category == "midnight_character":
        subject = get_random_midnight_character()
    else:
        subject = get_random_game_character()

    ROTATION_INDEX = (ROTATION_INDEX + 1) % len(CATEGORY_LIST)  # Move to next category
    return subject, category

# Function to generate funny questions using predefined or crossover templates
def generate_funny_question(subject, category):
    if category == "game_character":
        # Pick another random Midnight Club character for crossover questions
        mc_character = get_random_midnight_character()
        
        # Use crossover templates specifically for game characters + MC characters
        if CROSSOVER_QUESTIONS:
            template = random.choice(CROSSOVER_QUESTIONS)
            return template.format(subject, mc_character)
        
        # Fallback if no crossover questions are available
        return f"What would happen if {subject} met {mc_character} in Midnight Club?"

    # For other categories, randomly pick from predefined questions
    if PREDEFINED_QUESTIONS:
        template = random.choice(PREDEFINED_QUESTIONS)
        return template.format(subject)
    
    # Fallback if no predefined questions are available
    return f"Describe something sus about {subject}."

# Function to generate the challenge message
def generate_challenge():
    subject, category = get_random_subject()
    question = generate_funny_question(subject, category)
    return question

# Function to send the challenge to Discord Webhook and pin it
def send_challenge():
    challenge_message = generate_challenge()
    
    data = {
        # Format message for Discord
        "content": f"🌈 **Sus Comment Challenge!** 🌈\n💬 {challenge_message}\n\n🗳️ **Vote for the best response!** React with 🔥 or 💀.",
        "username": f"Sus Challenge Bot"
    }

    try:
        # Send message to Discord Webhook
        response = requests.post(WEBHOOK_URL, json=data)
        
        if response.status_code == 200:
            message_response = response.json()
            message_id = message_response.get("id")
            
            if message_id:
                pin_message(message_id)  # Pin the message
            
            logging.info("Challenge sent successfully!")
        
        else:
            logging.error(f"Failed to send challenge. Status Code: {response.status_code}, Response: {response.text}")
        
        # Send test webhook (for debugging)
        test_response = requests.post(TEST_WEBHOOK_URL, json=data)
        
        if test_response.status_code == 204:
            logging.info("Test challenge sent successfully!")
        else:
            logging.error(f"Failed to send test challenge. Status Code: {test_response.status_code}, Response: {test_response.text}")
    
    except Exception as e:
        logging.error(f"Error sending challenge to Discord: {e}")

# Function to pin a message in Discord using the bot token and channel ID
def pin_message(message_id):
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/pins/{message_id}"
    
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.put(url, headers=headers)
        
        if response.status_code == 204:
            logging.info("Message pinned successfully!")
        else:
            logging.error(f"Failed to pin message. Status Code: {response.status_code}, Response: {response.text}")
    
    except Exception as e:
        logging.error(f"Error pinning message: {e}")

# Main execution workflow (keeps pinning logic intact)
if __name__ == "__main__":
   send_challenge()
    
