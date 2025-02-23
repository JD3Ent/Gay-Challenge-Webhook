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
        mc_character = get_random_midnight_character()
        
        if CROSSOVER_QUESTIONS:
            template = random.choice(CROSSOVER_QUESTIONS)
            return template.format(subject, mc_character)
        
        return f"What would happen if {subject} met {mc_character} in Midnight Club?"

    elif category == "car":
        if CAR_SPECIFIC_QUESTIONS:
            template = random.choice(CAR_SPECIFIC_QUESTIONS)
            return template.format(subject)
        
        return f"Describe something sus about the car {subject}."

    else:  # For midnight_character or others, use general predefined questions
        if PREDEFINED_QUESTIONS:
            template = random.choice(PREDEFINED_QUESTIONS)
            return template.format(subject)
        
        return f"Describe something sus about {subject}."

# Function to generate the challenge message
def generate_challenge():
    subject, category = get_random_subject()
    question = generate_funny_question(subject, category)
    return question

# Function to calculate reactions and determine winners for the voting system
def calculate_reactions():
    try:
        if not os.path.exists(LAST_MESSAGE_ID_FILE):
            logging.info("No previous message ID found. Skipping reaction tally.")
            return None, None
        
        with open(LAST_MESSAGE_ID_FILE, 'r') as f:
            last_message_id = f.read().strip()
        
        url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages/{last_message_id}/reactions"
        
        headers = {
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}"
        }
        
        response = requests.get(url, headers=headers)
        
        pride_counts = {}
        skull_counts = {}
        
        if response.status_code == 200:
            message_data = response.json()
            
            for reaction in message_data.get("reactions", []):
                emoji_name = reaction["emoji"]["name"]
                
                if emoji_name == "🏳️‍🌈":
                    for user in requests.get(reaction["url"], headers=headers).json():
                        pride_counts[user["id"]] = pride_counts.get(user["id"], 0) + 1
                
                elif emoji_name == "💀":
                    for user in requests.get(reaction["url"], headers=headers).json():
                        skull_counts[user["id"]] = skull_counts.get(user["id"], 0) + 1
            
            gayest_user_id = max(pride_counts, key=pride_counts.get) if pride_counts else None
            token_straight_user_id = max(skull_counts, key=skull_counts.get) if skull_counts else None
            
            return gayest_user_id, token_straight_user_id
        
        else:
            logging.error(f"Failed to fetch message reactions. Status Code: {response.status_code}, Response: {response.text}")
            return None, None
    
    except Exception as e:
        logging.error(f"Error calculating reactions: {e}")
        return None, None

# Function to send the challenge to Discord Webhook and pin it
def send_challenge():
    challenge_message = generate_challenge()
    
    data = {
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

         # Calculate reactions before sending next question.
         gayest_user_id, token_straight_user_id = calculate_reactions()

         mention_messages = []

         if gayest_user_id is not None and token_straight_user_id is not None:
             mention_messages.append(f"<@{gayest_user_id}> you were the gayest of all for that last question! 🌈")
             mention_messages.append(f"<@{token_straight_user_id}> you were the token straight one in the server! 💀")
         
         if mention_messages: 
             mentions_content = "\n".join(mention_messages)
             requests.post(WEBHOOK_URL, json={"content": mentions_content})

         # Send test webhook (for debugging)
         test_response_data = {
             "content": f"[TEST] 🌈 **Sus Comment Challenge!** 🌈\n💬 {challenge_message}",
             "username": "Test Sus Challenge Bot"
         }
         test_response = requests.post(TEST_WEBHOOK_URL, json=test_response_data)

         if test_response.status_code == 204 or test_response.ok:
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
        
