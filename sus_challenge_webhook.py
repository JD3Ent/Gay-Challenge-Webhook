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
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # Hugging Face API Key
GIANTBOMB_API_KEY = os.getenv("GIANTBOMB_API_KEY")  # Giant Bomb API Key

# Hugging Face API Config
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/gpt2"
HUGGINGFACE_HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

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

QUESTION_TEMPLATES = {
    # Templates for fallback if AI fails or validation fails
    "car": [
        "{} just got a custom rainbow spoiler. What’s the most sus thing it could say about itself?",
        "{} is now the official car of a pride parade. How would it seduce the crowd?",
        "{} just got caught in a back alley doing something suspicious. What was it?",
        "{} has a secret compartment filled with... what? Make it as sus as possible.",
        "{} is now a contestant on RuPaul's Drag Race: Vehicle Edition. What’s its drag name?",
    ],
    "midnight_character": [
        "{} just confessed their wildest hookup story at midnight. What happened, and why is everyone blushing?",
        "{} is hosting a pride afterparty. What’s the most scandalous thing they’d do to entertain their guests?",
        "{} got caught sneaking out of someone else’s garage at 3 AM. What were they doing in there?",
        "{} is now starring in a gay romance movie. What’s the most dramatic scene they’d be in?",
        "{} just entered a drag competition. What’s their stage name, and what’s their signature move?",
    ],
    # Special templates for game character + Midnight Club character crossovers
    "game_character": [
        "{} just met {} in a Midnight Club game. Who would win in the most ridiculous street race ever?",
        "{} and {} are teaming up for a heist in Midnight Club. What’s their plan, and how does it go wrong?",
        "{} challenged {} to a dance-off at a pride parade. Who wins, and what’s their signature move?",
        "{} and {} are stuck in traffic together. What’s the most sus conversation they’d have?",
        "{} just stole {}’s car in Midnight Club. How does the chase end, and who gets away with what?",
    ],
}

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

# Function to validate AI-generated questions
def validate_question(question, subject):
    """
    Validate if the generated question makes sense.
    - Ensure it's not too short or too long.
    - Ensure it contains the subject.
    """
    if len(question) < 10 or len(question) > 200:
        logging.warning(f"Validation failed: Question length out of bounds ({len(question)} characters).")
        return False
    
    if subject not in question:
        logging.warning(f"Validation failed: Subject '{subject}' not found in question.")
        return False

    return True

# Function to generate funny questions using Hugging Face GPT-2 API or fallback templates
def generate_funny_question(subject, category):
    if category == "game_character":
        # Pick another random Midnight Club character for crossover questions
        mc_character = get_random_midnight_character()
        
        # Use crossover templates specifically for game characters + MC characters
        template = random.choice(QUESTION_TEMPLATES["game_character"])
        return template.format(subject, mc_character)
    
    prompt = f"Generate a funny LGBTQ+ or sus question about a {category}: {subject}."
    
    payload = {
        "inputs": prompt,
        # Add parameters for better control over generation
        # Lower temperature for less randomness, limit max_length to prevent verbosity
        # Top_k/top_p to control sampling diversity
        "parameters": {
            "temperature": 0.7,
            "max_length": 50,
            "top_k": 50,
            "top_p": 0.9,
            # Avoid repetition by penalizing repeated sequences
            "repetition_penalty": 1.2,
        },
        # Options to ensure clean outputs (e.g., no unfinished sentences)
        "options": {"use_cache": True, "wait_for_model": True},
    }

    try:
        response = requests.post(HUGGINGFACE_API_URL, headers=HUGGINGFACE_HEADERS, json=payload)
        
        if response.status_code != 200:
            raise ValueError(f"API returned non-200 status code: {response.status_code}")
        
        result = response.json()
        
        if isinstance(result, dict) and result.get("generated_text"):
            generated_question = result["generated_text"]
            logging.info(f"AI Response: {generated_question}")
            
            # Validate the generated question
            if validate_question(generated_question, subject):
                return generated_question
        
        raise ValueError("Unexpected API response format or validation failed.")
    
    except Exception as e:
        logging.error(f"Hugging Face API Error: {e}")
        
        # Fallback to predefined templates if AI fails or validation fails
        template = random.choice(QUESTION_TEMPLATES[category])
        return template.format(subject)

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
    
