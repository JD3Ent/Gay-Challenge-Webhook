import requests
import random
import os

# Load environment variables
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Discord Webhook (Main)
TEST_WEBHOOK_URL = os.getenv("TEST_WEBHOOK_URL")  # Webhook.site URL for testing/debugging
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Bot token for pinning messages
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Discord Channel ID
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

CATEGORY_LIST = ["car", "midnight_character"]

ROTATION_INDEX = (len(CATEGORY_LIST) + 1) % len(CATEGORY_LIST) # Used to rotate categories

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

# Function to generate the challenge message dynamically
def generate_challenge():
    subject, category = get_random_subject()
    question = generate_funny_question(subject, category)
    
    
    # Add emojis, formatting, and the role mention
    challenge_message_content = (
        f"🌈 **Sus Comment Challenge!** 🌈\n\n"
        f"💬 **{question}**\n\n"
        f"🗳️ **Vote for the best reply <@&1343147761595449374>!** React with 🏳️‍🌈 or 💀 for Gayest Or Token Straightest response!"
    )
    
    return challenge_message_content

# Function to send a message to a webhook URL (main or test)
def send_webhook_message(webhook_url, content):
    try:
        response = requests.post(webhook_url, json={"content": content})
        if response.status_code in [200, 204]:
            print(f"Message sent successfully to {webhook_url}.")
            return response.json().get("id") if response.content else None  # Return message ID if available
        else:
            print(f"Failed to send message. Status Code: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

# Function to pin a message in Discord using the bot token and channel ID
def pin_message(message_id):
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/pins/{message_id}"
    
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        print(f"Attempting to pin message with ID: {message_id}")
        response = requests.put(url, headers=headers)

        if response.status_code == 204:
            print("Message pinned successfully!")
        else:
            print(f"Failed to pin message. Status Code: {response.status_code}, Response: {response.text}")

    except Exception as e:
        print(f"Error pinning message: {e}")

# Function to fetch replies to a specific message ID in Discord
def fetch_replies(message_id):
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages?around={message_id}&limit=50"
    
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            messages = response.json()
            replies = [msg for msg in messages if msg.get("referenced_message", {}).get("id") == message_id]
            print(f"Fetched {len(replies)} replies.")
            return replies

        else:
            print(f"Failed to fetch replies. Status Code: {response.status_code}, Response: {response.text}")
            return []

    except Exception as e:
        print(f"Error fetching replies: {e}")
        return []

# Function to tally reactions on replies and determine winners/losers
def tally_reactions_on_replies(message_id):
    replies = fetch_replies(message_id)

    pride_counts = {}
    skull_counts = {}

    for reply in replies:
        reactions = reply.get("reactions", [])
        
        for reaction in reactions:
            emoji_name = reaction["emoji"]["name"]
            count = reaction["count"]
            
            user_id = reply["author"]["id"]  # Get the user who made this reply
            
            if emoji_name == "🏳️‍🌈":
                pride_counts[user_id] = pride_counts.get(user_id, 0) + count
            elif emoji_name == "💀":
                skull_counts[user_id] = skull_counts.get(user_id, 0) + count

    gayest_user_id = max(pride_counts, key=pride_counts.get) if pride_counts else None
    token_straight_user_id = max(skull_counts, key=skull_counts.get) if skull_counts else None

    return gayest_user_id, token_straight_user_id

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

# Main function to send challenge and handle reactions/winners/losers
def send_challenge():
    last_message_id = load_last_message_id()

    # Tally reactions from replies before sending a new challenge
    if last_message_id:
        gayest_user_id, token_straight_user_id = tally_reactions_on_replies(last_message_id)

        # Announce winners/losers if available
        if gayest_user_id or token_straight_user_id:
            winner_message_parts = []
            
            if gayest_user_id:
                winner_message_parts.append(f"<@{gayest_user_id}> was the gayest of all! 🌈")
            
            if token_straight_user_id:
                winner_message_parts.append(f"<@{token_straight_user_id}> was the token straight one! 💀")

            winner_announcement_content = "\n".join(winner_message_parts)
            
            send_webhook_message(WEBHOOK_URL, winner_announcement_content)

    # Generate new challenge message dynamically with proper formatting
    challenge_message_content = generate_challenge()

    # Send main challenge message and get its ID
    new_message_id = send_webhook_message(WEBHOOK_URL, challenge_message_content)

    if new_message_id:
        # Pin the new challenge message in Discord
        pin_message(new_message_id)

        # Save last message ID for future reaction tallying
        save_last_message_id(new_message_id)

    # Send test webhook (for debugging purposes only to TEST_WEBHOOK_URL)
    test_content = f"[TEST] 🌈 Test Sus Comment Challenge Sent!\n💬 {challenge_message_content}"
    send_webhook_message(TEST_WEBHOOK_URL, test_content)

if __name__ == "__main__":
    send_challenge()

