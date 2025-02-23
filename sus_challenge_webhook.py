import requests
import random
import os

# Load environment variables
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Discord Webhook
TEST_WEBHOOK_URL = os.getenv("TEST_WEBHOOK_URL")  # Webhook.site URL for testing
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Bot token for pinning messages
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")  # Discord Channel ID
LAST_MESSAGE_ID_FILE = "last_message_id.txt"  # File to store last message ID

# File paths for external data
MC_CARS_FILE = "mc_cars.txt"
MC_CHARACTERS_FILE = "mc_characters.txt"
QUESTIONS_FILE = "questions.txt"
CROSSOVER_FILE = "crossover.txt"
CAR_SPECIFIC_FILE = "cars.txt"

# Function to load data from a file
def load_data(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return []

# Load Midnight Club cars, characters, and questions from external files
MIDNIGHT_CLUB_CARS = load_data(MC_CARS_FILE)
MIDNIGHT_CLUB_CHARACTERS = load_data(MC_CHARACTERS_FILE)
PREDEFINED_QUESTIONS = load_data(QUESTIONS_FILE)
CROSSOVER_QUESTIONS = load_data(CROSSOVER_FILE)
CAR_SPECIFIC_QUESTIONS = load_data(CAR_SPECIFIC_FILE)

CATEGORY_LIST = ["car", "midnight_character", "game_character"]
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
    else:
        subject = f"Game Character #{random.randint(1, 100)}"  # Placeholder for game characters

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

# Function to generate the challenge message dynamically
def generate_challenge():
    subject, category = get_random_subject()
    question = generate_funny_question(subject, category)
    return question

# Function to load the last message ID from file
def load_last_message_id():
    if os.path.exists(LAST_MESSAGE_ID_FILE):
        with open(LAST_MESSAGE_ID_FILE, 'r') as f:
            return f.read().strip()
    return None

# Function to save the last message ID to file
def save_last_message_id(message_id):
    with open(LAST_MESSAGE_ID_FILE, 'w') as f:
        f.write(message_id)

# Function to tally reactions and determine winners/losers
def tally_reactions():
    last_message_id = load_last_message_id()
    if not last_message_id:
        print("No previous message ID found. Skipping reaction tally.")
        return None, None

    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages/{last_message_id}/reactions"
    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch reactions. Status Code: {response.status_code}, Response: {response.text}")
            return None, None

        pride_counts = {}
        skull_counts = {}

        for reaction in response.json():
            emoji_name = reaction["emoji"]["name"]
            users_url = reaction["url"]

            users_response = requests.get(users_url, headers=headers)
            if users_response.status_code == 200:
                users = users_response.json()
                for user in users:
                    if emoji_name == "🏳️‍🌈":
                        pride_counts[user["id"]] = pride_counts.get(user["id"], 0) + 1
                    elif emoji_name == "💀":
                        skull_counts[user["id"]] = skull_counts.get(user["id"], 0) + 1

        gayest_user_id = max(pride_counts, key=pride_counts.get) if pride_counts else None
        token_straight_user_id = max(skull_counts, key=skull_counts.get) if skull_counts else None

        return gayest_user_id, token_straight_user_id

    except Exception as e:
        print(f"Error tallying reactions: {e}")
        return None, None

# Function to pin a message in Discord using the bot token and channel ID
def pin_message(message_id):
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/pins/{message_id}"
    
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        print(f"Attempting to pin message with ID: {message_id}")  # Debugging
        response = requests.put(url, headers=headers)

        if response.status_code == 204:
            print("Message pinned successfully!")
        else:
            print(f"Failed to pin message. Status Code: {response.status_code}, Response: {response.text}")

    except Exception as e:
        print(f"Error pinning message: {e}")

# Function to send a challenge message and pin it
def send_challenge():
    gayest_user_id, token_straight_user_id = tally_reactions()

    # Announce winners/losers if available
    if gayest_user_id or token_straight_user_id:
        winner_message_parts = []
        if gayest_user_id:
            winner_message_parts.append(f"<@{gayest_user_id}> was the gayest of all! 🌈")
        if token_straight_user_id:
            winner_message_parts.append(f"<@{token_straight_user_id}> was the token straight one! 💀")

        winner_announcement = "\n".join(winner_message_parts)
        data_winner_announcement = {"content": winner_announcement}
        
        response_winner_announcement = requests.post(WEBHOOK_URL, json=data_winner_announcement)
        
        print("Winner announcement sent!" if response_winner_announcement.ok else response_winner_announcement.text)

    # Generate new challenge message dynamically
    challenge_message_content = generate_challenge()
    
    data_new_challenge = {"content": challenge_message_content}
    
    try:
        # Send new challenge message
        response_new_challenge = requests.post(WEBHOOK_URL, json=data_new_challenge)

        if response_new_challenge.status_code == 200 or response_new_challenge.status_code == 204:
            print("Challenge sent successfully!")
            
            # Extract message ID and save it for future reference
            message_response_json = response_new_challenge.json()
            message_id_new_challenge = message_response_json.get("id")
            
            if message_id_new_challenge:
                save_last_message_id(message_id_new_challenge)
                print(f"Message ID saved: {message_id_new_challenge}")
                
                # Pin the new challenge message
                pin_message(message_id_new_challenge)

                # Send test webhook (for debugging purposes)
                test_data_content={"content":f"[TEST] Sent: {challenge_message_content}"}
                test_response = requests.post(TEST_WEBHOOK_URL, json=test_data_content)

                print("Test challenge sent successfully!" if test_response.ok else test_response.text)

        
        else:
            print(f"Failed to send challenge. Status Code: {response_new_challenge.status_code}, Response: {response_new_challenge.text}")

    except Exception as e:
        print(f"Error sending challenge: {e}")

# Main execution workflow
if __name__ == "__main__":
   send_challenge()
    
