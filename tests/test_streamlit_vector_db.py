import pytest
import json
import numpy as np
from unittest.mock import patch, MagicMock
from sentence_transformers import SentenceTransformer

# Import the functions from the main module
from streamlit_vector_db import (
    load_json,
    prepare_content,
    add_content_to_collection,
    get_user_embedding,
    match_user_to_content,
    process_all_users,
    filter_recommendations
)

# Mock data
mock_content_data = [
    {"id": "1", "content": "Sample content 1", "tags": [{"value": "tag1"}], "category": "news"},
    {"id": "2", "content": "Sample content 2", "tags": [{"value": "tag2"}], "category": "sports"}
]

mock_user_data = [
    {"name": "user1", "interests": [{"type": "tag", "value": "tag1", "threshold": 0.8}]},
    {"name": "user2", "interests": [{"type": "tag", "value": "tag2", "threshold": 0.5}]}
]

mock_embeddings = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

@pytest.fixture
def mock_model():
    with patch('streamlit_vector_db.SentenceTransformer') as mock_model:
        instance = mock_model.return_value
        instance.encode.return_value = mock_embeddings
        yield instance

def test_load_json(tmp_path):
    # Create a temporary JSON file
    data = {"key": "value"}
    file_path = tmp_path / "data.json"
    with open(file_path, 'w') as file:
        json.dump(data, file)
    
    # Test load_json function
    assert load_json(file_path) == data

def test_prepare_content(mock_model):
    content_ids, content_full_texts, content_embeddings, metadata = prepare_content(mock_content_data)
    
    assert content_ids == ["1", "2"]
    assert content_full_texts == ["Sample content 1", "Sample content 2"]
    # assert np.array_equal(content_embeddings, mock_embeddings)
    assert metadata == [
        {"id": "1", "category": "news", "interests": "tag1"},
        {"id": "2", "category": "sports", "interests": "tag2"}
    ]

def test_add_content_to_collection():
    mock_collection = MagicMock()
    content_ids = ["1", "2"]
    content_full_texts = ["Sample content 1", "Sample content 2"]
    content_embeddings = mock_embeddings
    metadata = [
        {"id": "1", "category": "news", "interests": "tag1"},
        {"id": "2", "category": "sports", "interests": "tag2"}
    ]
    
    add_content_to_collection(mock_collection, content_ids, content_full_texts, content_embeddings, metadata)
    mock_collection.add.assert_called_once_with(
        ids=content_ids,
        documents=content_full_texts,
        embeddings=content_embeddings.tolist(),
        metadatas=metadata
    )


def test_match_user_to_content(mock_model):
    mock_collection = MagicMock()
    mock_collection.query.return_value = {"documents": [["doc1"]], "distances": [[0.1]], "ids": [["1"]]}
    
    interests = [{"type": "tag", "value": "tag1", "threshold": 0.8}]
    results = match_user_to_content(mock_collection, "user1", interests, top_n=1)
    
    assert results == {"documents": [["doc1"]], "distances": [[0.1]], "ids": [["1"]]}

@patch('streamlit_vector_db.load_json')
@patch('streamlit_vector_db.match_user_to_content')
def test_process_all_users(mock_match_user_to_content, mock_load_json):
    mock_load_json.return_value = mock_user_data
    mock_match_user_to_content.return_value = {"documents": [["doc1"]], "distances": [[0.1]], "ids": [["1"]]}
    
    mock_collection = MagicMock()
    user_recommendations = process_all_users(mock_collection, "dummy_path", top_n=1)
    
    expected_recommendations = {
        "user1": {"documents": [["doc1"]], "distances": [[0.1]], "ids": [["1"]]},
        "user2": {"documents": [["doc1"]], "distances": [[0.1]], "ids": [["1"]]}
    }
    assert user_recommendations == expected_recommendations

def test_filter_recommendations():
    recommendations = {
        "documents": [["doc1", "doc2"]],
        "distances": [[0.1, 0.2]],
        "ids": [["1", "2"]]
    }
    user_interests = [{"type": "tag", "value": "tag1", "threshold": 0.8}]
    selected_interests = ["tag"]
    metadata = [
        {"id": "1", "category": "news", "interests": "tag1"},
        {"id": "2", "category": "sports", "interests": "tag2"}
    ]
    
    filtered_docs = filter_recommendations(recommendations, user_interests, selected_interests, metadata)
    expected_docs = [(1, "1", "doc1", 0.9, "tag1"), (2, "2", "doc2", 0.8, "tag2")]
    
    assert filtered_docs == expected_docs
