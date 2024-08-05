import json
import random
from transformers import pipeline

# Load the text generation pipeline with pad_token_id set to eos_token_id
generator = pipeline('text-generation', model='gpt2', pad_token_id=50256)

# Expanded list of possible interest types
INTEREST_TYPES = [
    "instrument", "hobby", "technology", "food", "sport", "music", 
    "art", "travel", "finance", "literature", "science", "health", "fitness", 
    "gaming", "photography", "cooking", "crafting", "fashion", "history", 
    "politics", "environment", "volunteering", "movies", "theater", "dance", 
    "comics", "podcasts", "writing", "outdoor activities", "collecting", 
    "spirituality", "home improvement", "pets"
]

countries = ["United States", "Canada", "Germany", "Japan", "Brazil", "United Kingdom", "Italy"]

def generate_value(interest_type):
    """Generate a value for the given interest type using Hugging Face model."""
    prompt = f"A realistic {interest_type} could be: "
    result = generator(prompt, max_length=30, num_return_sequences=1, do_sample=True, top_k=50)
    
    # Extract the generated text and clean it up
    generated_text = result[0]['generated_text'].strip()
    
    # Remove the prompt part from the generated text
    if generated_text.startswith(prompt):
        generated_text = generated_text[len(prompt):].strip()
    
    # Further clean the output to ensure it doesn't contain unwanted phrases
    value = generated_text.split('.')[0].strip()  # Take the first sentence
    
    # Check if the generated value is appropriate
    if value.lower() in ["a realistic", "a realistic {interest_type} could be:"]:
        return "Unknown Value"  # If the model couldn't generate a proper value, return a default
    else:
        return value

def generate_user():
    """Generate a single user with a name and a list of interests."""
    name = f"User {random.randint(1, 100000)}"  # Simple name generation for demonstration
    
    # Generate the country interest first
    country_interest = {
        "type": "country",
        "value": random.choice(countries),
        "threshold": round(random.uniform(0, 1), 2)
    }
    
    # Generate other interests, ensuring the country interest is included only once
    other_interests = []
    num_other_interests = random.randint(1, 4)  # Generate 1 to 4 other interests

    # Generate other interests without including "country"
    for _ in range(num_other_interests):
        interest_type = random.choice(INTEREST_TYPES)
        value = generate_value(interest_type)
        threshold = round(random.uniform(0, 1), 2)
        other_interests.append({
            "type": interest_type,
            "value": value,
            "threshold": threshold
        })

    # Combine the country interest with other interests
    interests = [country_interest] + other_interests
    return {"name": name, "interests": interests}

def generate_users(num_users):
    """Generate a list of users."""
    users = [generate_user() for _ in range(num_users)]
    return users

# Generate 100 users
users = generate_users(100)

# Save to JSON file
with open("users.json", "w") as f:
    json.dump(users, f, indent=4)

print("Generated users.json with synthetic data.")
