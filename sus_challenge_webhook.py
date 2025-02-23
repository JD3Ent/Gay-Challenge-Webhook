import requests
import random
import os
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Discord Webhook
TEST_WEBHOOK_URL = os.getenv("TEST_WEBHOOK_URL")  # Webhook.site URL for testing
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Bot token for pinning and fetching messages
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")  # Discord Channel ID
GIANTBOMB_API_KEY = os.getenv("GIANTBOMB_API_KEY")  # Giant Bomb API Key

# File paths for external data
MC_CARS_FILE = "mc_cars.txt"
MC_CHARACTERS_FILE = "mc_characters.txt"
LAST_MESSAGE_ID_FILE = "last_message_id.txt"

# Load data from an external file
def load_data(file_path):
    try:
        with open(file_path, 'r') as f:
            data = [line.strip() for line in f if line.strip()]
            logging.info(f"Loaded {len(data)} items from {file_path}")
            return data
    except Exception as e:
        logging.error(f"Error loading data from {file_path}: {e}")
        return []

# Load Midnight Club cars and characters from external files
MIDNIGHT_CLUB_CARS = load_data(MC_CARS_FILE)
MIDNIGHT_CLUB_CHARACTERS = load_data(MC_CHARACTERS_FILE)

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
CAR_SPECIFIC_QUESTIONS = load_questions("cars.txt")

CATEGORY_LIST = ["car", "midnight_character", "game_character"]

ROTATION_INDEX = 0  # Used to rotate categories

# Function to fetch a random car
def get_random_car():
    if MIDNIGHT_CLUB_CARS:
        return random.choice(MIDNIGHT_CLUB_CARS)
    else:
        logging.warning("No cars available. Returning default fallback.")
        return "Generic Car"

# Function to fetch a random Midnight Club character
def get_random_midnight_character():
    if MIDNIGHT_CLUB_CHARACTERS:
        return random.choice(MIDNIGHT_CLUB_CHARACTERS)
    else:
        logging.warning("No characters available. Returning default fallback.")
        return "Generic Character"

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
        return get_random_midnight_character()  # Fallback to an MC character

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

    elif category == "car":
        # Use car-specific templates for cars
        if CAR_SPECIFIC_QUESTIONS:
            template = random.choice(CAR_SPECIFIC_QUESTIONS)
            return template.format(subject)
        
        # Fallback if no car-specific questions are available
        return f"Describe something sus about the car {subject}."

    else:  # For midnight_character or others, use general predefined questions
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
        # Send message to Discord Webhook and store message ID for reactions later
        response = requests.post(WEBHOOK_URL, json=data)
        
        if response.status_code == 200:
            message_response = response.json()
            message_id = message_response.get("id")
            
            if message_id:
                with open(LAST_MESSAGE_ID_FILE, 'w') as f:
                    f.write(message_id)  # Save the last message ID
            
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
     url
    
