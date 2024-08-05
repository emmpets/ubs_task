import json

# Load users and content from JSON files
def load_data():
    with open('users.json', 'r') as f:
        users = json.load(f)
    with open('content.json', 'r') as f:
        content = json.load(f)
    return users, content

# Match content with user interests
def match_country_content(users, content):
    user_content = {}
    for user in users:
        relevant_content = []
        user_interests = user['interests']

        for item in content:
            # Check if the content has tags
            if 'tags' in item:
                for tag in item['tags']:
                    # Match based on same interest type and country
                    for interest in user_interests:
                        # Check if the interest is a country and matches the tag
                        if (interest['type'] == 'country' and
                                tag['type'] == 'country' and
                                tag['value'] == interest['value']):
                            relevant_content.append(item)
                            break  # Stop checking other interests for this item
                        # Check if the interest is of another type and matches the tag
                        elif (interest['type'] != 'country' and
                                tag['type'] == interest['type'] and
                                tag['value'] == interest['value']):
                            relevant_content.append(item)
                            break  # Stop checking other interests for this item
        user_content[user['name']] = relevant_content
    return user_content


# Match content with user interests
def match_country_and_content(users, content):
    user_content = {}
    for user in users:
        relevant_content = []
        user_interests = user['interests']

        # Initialize flags for matching conditions
        country_match = False
        other_interests_match = False

        for item in content:
            # Check if the content has tags
            if 'tags' in item:
                # Reset flags for each content item
                country_match = False
                other_interests_match = False

                # Check for country interest matches
                for interest in user_interests:
                    if interest['type'] == 'country':
                        for tag in item['tags']:
                            if tag['type'] == 'country' and tag['value'] == interest['value']:
                                country_match = True
                                break  # Stop checking tags for country match
                    if country_match:
                        break  # Stop checking interests if country match is found

                # Check for other types of interest matches
                for interest in user_interests:
                    if interest['type'] != 'country':
                        for tag in item['tags']:
                            if tag['type'] == interest['type'] and tag['value'] == interest['value']:
                                other_interests_match = True
                                break  # Stop checking tags for other interest match
                    if other_interests_match:
                        break  # Stop checking interests if other match is found

                # Only add content if both conditions are met
                if country_match and other_interests_match:
                    relevant_content.append(item)

        user_content[user['name']] = relevant_content
    return user_content
