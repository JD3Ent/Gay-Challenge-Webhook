import requests
import random
import os

# Load environment variables
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Discord Webhook
TEST_WEBHOOK_URL = os.getenv("TEST_WEBHOOK_URL")  # Webhook.site URL for testing
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Bot token for pinning messages
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")  # Discord Channel ID

# File paths for external data
MC_CARS_FILE = "mc_cars.txt"
MC_CHARACTERS_FILE = "mc_characters.txt"
LAST_MESSAGE_ID_FILE = "last_message_id.txt"

# Load data from an external file
def load_data(file_path):
    try:
        with open(file_path, 'r') as f:
            data = [line.strip() for line in f if line.strip()]
            return data
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return []

# Load Midnight Club cars and characters from external files
MIDNIGHT_CLUB_CARS = load_data(MC_CARS_FILE)
MIDNIGHT_CLUB_CHARACTERS = load_data(MC_CHARACTERS_FILE)

# Load questions from an external file
def load_questions(file_path):
    try:
        with open(file_path, 'r') as f:
            questions = [line.strip() for line in f if line.strip()]
            return questions
    except Exception as e:
        print(f"Error loading questions from {file_path}: {e}")
        return []

# Load all predefined questions at startup
PREDEFINED_QUESTIONS = load_questions("questions.txt")
CROSSOVER_QUESTIONS = load_questions("crossover.txt")
CAR_SPECIFIC_QUESTIONS = load_questions("cars.txt")

CATEGORY_LIST = ["car", "midnight_character"]

ROTATION_INDEX = 0  # Used to rotate categories

# Function to fetch a random car
def get_random_car():
    if MIDNIGHT_CLUB_CARS:
        return random.choice(MIDNIGHT_CLUB_CARS)
    else:
        return "Generic Car"

# Function to fetch a random Midnight Club character
def get_random_midnight_character():
    if MIDNIGHT_CLUB_CHARACTERS:
        return random.choice(MIDNIGHT_CLUB_CHARACTERS)
    else:
        return "Generic Character"

# Function to rotate between categories (preserves rotation logic)
def get_random_subject():
    global ROTATION_INDEX
    category = CATEGORY_LIST[ROTATION_INDEX]
    
    if category == "car":
        subject = get_random_car()
    elif category == "midnight_character":
        subject = get_random_midnight_character()

    ROTATION_INDEX = (ROTATION_INDEX + 1) % len(CATEGORY_LIST)  # Move to next category
    return subject, category

# Function to generate funny questions using predefined or crossover templates
def generate_funny_question(subject, category):
    if category == "car":
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
            print("Message pinned successfully!")
        else:
            print(f"Failed to pin message. Status Code: {response.status_code}, Response: {response.text}")

    except Exception as e:
        print(f"Error pinning message: {e}")

# Function to send the challenge to Discord Webhook and test Webhook
def send_challenge():
    challenge_message = generate_challenge()
    
    data = {
        "content": f"🌈 **Sus Comment Challenge!** 🌈\n💬 {challenge_message}\n\n🗳️ **Vote for the best response!** React with 🔥 or 💀.",
        "username": f"Sus Challenge Bot"
    }

    try:
        # Send message to Discord Webhook and store message ID for reactions later
        response = requests.post(WEBHOOK_URL, json=data)

        if response.status_code == 200 or response.status_code == 204:
            print("Challenge sent successfully!")
            
            # Extract message ID and save it for pinning later
            message_response = response.json()
            message_id = message_response.get("id")
            
            if message_id:
                with open(LAST_MESSAGE_ID_FILE, 'w') as f:
                    f.write(message_id)  # Save the last message ID
                
                # Pin the message in Discord
                pin_message(message_id)
        
        else:
            print(f"Failed to send challenge. Status Code: {response.status_code}, Response: {response.text}")

        # Send test webhook (for debugging)
        test_response_data = {
            "content": f"[TEST] 🌈 **Sus Comment Challenge!** 🌈\n💬 {challenge_message}",
            "username": "Test Sus Challenge Bot"
        }
        test_response = requests.post(TEST_WEBHOOK_URL, json=test_response_data)

        if test_response.status_code == 204 or test_response.ok:
            print("Test challenge sent successfully!")
        else:
            print(f"Failed to send test challenge. Status Code: {test_response.status_code}, Response: {test_response.text}")

    except Exception as e:
        print(f"Error sending challenge to Discord: {e}")

# Main execution workflow
if __name__ == "__main__":
   send_challenge()
    
