import json
import random
from transformers import pipeline, set_seed

# Define the interest types and countries
INTEREST_TYPES = [
    "instrument", "hobby", "technology", "food", "sport", "music", 
    "art", "travel", "finance", "literature", "science", "health", "fitness", 
    "gaming", "photography", "cooking", "crafting", "fashion", "history", 
    "politics", "environment", "volunteering", "movies", "theater", "dance", 
    "comics", "podcasts", "writing", "outdoor activities", "collecting", 
    "spirituality", "home improvement", "pets"
]

COUNTRIES = ["United States", "Canada", "Germany", "Japan", "Brazil", "United Kingdom", "Italy"]

# Initialize the GPT-2 text generation pipeline
generator = pipeline('text-generation', model='gpt2')
set_seed(42)

def generate_json_data(num_entries):
    data = []
    
    for i in range(num_entries):
        # Randomly choose an interest and a country
        interest = random.choice(INTEREST_TYPES)
        country = random.choice(COUNTRIES)
        prompt = f"Generate content about {interest} in {country}."
        
        # Generate content using GPT-2
        generated_content = generator(prompt, max_length=100, num_return_sequences=1)[0]['generated_text']
        
        # Remove the prompt from the generated content
        # We can split the generated content by the first period to get the relevant part
        if '.' in generated_content:
            generated_content = generated_content.split('.', 1)[1].strip()  # Get text after the first period
        else:
            generated_content = generated_content.strip()  # If no period, just strip whitespace

        entry = {
            "id": str(i + 1),
            "title": f"My title {i + 1}",
            "content": generated_content,
            "tags": [
                {
                    "type": "interest",
                    "value": interest,
                    "threshold": round(random.uniform(0.1, 1.0), 2)
                },
                {
                    "type": "country",
                    "value": country,
                    "threshold": round(random.uniform(0.1, 1.0), 2)
                }
            ]
        }
        data.append(entry)
    
    return data

def save_to_json_file(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Generate JSON data with 1000 entries
json_data = generate_json_data(1000)

# Save the data to a JSON file
save_to_json_file(json_data, 'content.json')

print("Data has been saved to content.json")