import streamlit as st
from functions.helper_functions import load_data, match_country_content

# Main application
def main():
    st.title("User Content Matcher")

    users, content = load_data()
    user_content = match_country_content(users, content)

    # Dropdown for selecting a user
    user_names = [user['name'] for user in users]
    selected_user = st.selectbox("Select a user:", user_names)

    # Display selected user's interests
    user_info = next(user for user in users if user['name'] == selected_user)
    st.subheader(f"{selected_user}'s Interests:")
    interests = user_info['interests']
    for interest in interests:
        if interest['type'] == 'country':
            st.write(f"- {interest['type']}: {interest['value']} (Threshold: {interest['threshold']})")
        else:
            st.write(f"- {interest['type']}: (Threshold: {interest['threshold']})")

    # Display selected user's relevant content
    st.subheader(f"Relevant Content for {selected_user}:")
    relevant_content = user_content.get(selected_user, [])
    
    # Sort relevant content based on priority (assuming 'priority' is a key in each content item)
    relevant_content.sort(key=lambda x: x.get('priority', 0), reverse=True)

    # Dropdown for selecting the number of top contents to display
    top_n_options = [1, 3, 5, 10, 15, 25]
    max_display = min(len(relevant_content), max(top_n_options))  # Limit to a maximum of the highest option
    top_n = st.selectbox("Select number of top contents to display:", 
                         [option for option in top_n_options if option <= max_display])

    # Display the top N relevant content with numbering
    if relevant_content:
        for index, item in enumerate(relevant_content[:top_n], start=1):
            # Get interests associated with the content
            content_interests = item.get('tags', [])
            interests_str = ', '.join([f"{tag['type']}: {tag['value']}" for tag in content_interests])
            # Display title with interests in parentheses and numbering
            st.write(f"{index}. **{item['title']}** ({interests_str}): {item['content']}")
    else:
        st.write("No relevant content found.")

if __name__ == "__main__":
    main()
