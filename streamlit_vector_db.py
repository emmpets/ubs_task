import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import streamlit as st

# Load the pre-trained SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_json(file_path):
    """Load data from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def prepare_content(content_data):
    """Prepare content for embedding and metadata extraction."""
    content_full_texts = [item['content'] for item in content_data]
    content_ids = [item['id'] for item in content_data]
    content_embeddings = model.encode(content_full_texts)
    
    # Create metadata as a list of dictionaries
    metadata = []
    for item in content_data:
        # Join interest values into a single string
        interest_values = [tag['value'] for tag in item.get('tags', [])]
        metadata.append({
            "id": item['id'],
            "category": item.get('category', 'general'),
            "interests": ', '.join(interest_values)  # Join interests into a single string
        })
    
    return content_ids, content_full_texts, content_embeddings, metadata

def add_content_to_collection(collection, content_ids, content_full_texts, content_embeddings, metadata):
    """Add content and metadata to the ChromaDB collection."""
    collection.add(
        ids=content_ids,
        documents=content_full_texts,
        embeddings=content_embeddings.tolist(),
        metadatas=metadata
    )

def get_user_embedding(interests):
    """Generate a user embedding based on their interests."""
    interest_values = [interest['value'] for interest in interests]
    interest_embeddings = model.encode(interest_values)
    return np.mean(interest_embeddings, axis=0)

def match_user_to_content(collection, user_id, interests, top_n=3):
    """Match a user to content based on their interests."""
    user_embedding = get_user_embedding(interests)
    results = collection.query(
        query_embeddings=[user_embedding.tolist()],
        n_results=top_n
    )
    return results

def process_all_users(collection, file_path, top_n):
    """Process all users and generate recommendations."""
    user_recommendations = {}
    users = load_json(file_path)

    for user in users:
        user_id = user['name']
        interests = user['interests']
        recommendations = match_user_to_content(collection, user_id, interests, top_n)
        user_recommendations[user_id] = recommendations
    
    return user_recommendations

def filter_recommendations(recommendations, user_interests, selected_interests, metadata):
    """Filter recommendations based on selected interest types."""
    filtered_docs = []
    for index, (doc, score, doc_id) in enumerate(zip(recommendations['documents'][0], recommendations['distances'][0], recommendations['ids'][0])):
        # Check if the interest type is in the selected interests
        if any(interest['type'] in selected_interests for interest in user_interests):
            # Get the interest value from the metadata
            interest_value = next((meta['interests'] for meta in metadata if meta['id'] == doc_id), None)
            filtered_docs.append((index + 1, doc_id, doc, 1 - score, interest_value))
    return filtered_docs

if __name__ == "__main__":
    # Paths to the JSON files
    users_json_file_path = './data/users.json'
    content_json_file_path = './data/content.json'
    
    # Initialize ChromaDB client
    client = chromadb.Client()
    
    # Check if the collection already exists
    collection_name = "user_interests"
    try:
        collection = client.get_collection(collection_name)
    except Exception:
        # If the collection does not exist, create it
        collection = client.create_collection(collection_name)

    # Load and prepare content data
    content_data = load_json(content_json_file_path)
    content_ids, content_full_texts, content_embeddings, metadata = prepare_content(content_data)
    
    # Add content to the collection
    add_content_to_collection(collection, content_ids, content_full_texts, content_embeddings, metadata)
    
    # Streamlit dashboard
    st.set_page_config(page_title="Content Recommendations")
    st.title("Content Recommendations")

    # Create a dropdown menu for selecting users
    users = load_json(users_json_file_path)
    user_names = [user['name'] for user in users]
    selected_user = st.selectbox("Select a user", user_names)

    # Create a dropdown menu for selecting the number of recommendations
    top_n = st.selectbox("Select the number of top recommendations", [1, 3, 5, 10], index=1)

    # Find the selected user and display their interests
    user_info = next(user for user in users if user['name'] == selected_user)
    st.subheader(f"User Interests for {selected_user}:")
    for interest in user_info['interests']:
        if interest['type'] == 'country':
            st.write(f"- {interest['type']}: {interest['value']} (Threshold: {interest['threshold']})")
        else:
            st.write(f"- {interest['type']}: (Threshold: {interest['threshold']})")

    # Create a multiselect for selecting interest types
    interest_types = [interest['type'] for interest in user_info['interests']]
    selected_interest_types = st.multiselect("Select interest types to filter", interest_types, default=interest_types)

    # Display recommendations for the selected user
    st.subheader(f"Recommendations for {selected_user}:")
    recommendations = process_all_users(collection, users_json_file_path, top_n)[selected_user]

    # Filter recommendations based on selected interest types
    filtered_recommendations = filter_recommendations(recommendations, user_info['interests'], selected_interest_types, metadata)

    # Display filtered recommendations
    if filtered_recommendations:
        for index, doc_id, doc, score, interest_value in filtered_recommendations:
            if score < 1:  # Only show documents with similarity > 0
                st.write(f"{index}. ID: {doc_id}, (similarity: {score:.2f})")
                st.write(f"Document Tags: {interest_value}")
                st.write(f"Document Context: {doc}")
    else:
        st.write("No recommendations found based on the selected interest types.")