import json
import random
from transformers import pipeline
import pytest

from generate_synth_data.generate_users_hf import generate_value, generate_user, generate_users, INTEREST_TYPES, countries

def test_generate_value():
    for interest_type in INTEREST_TYPES:
        value = generate_value(interest_type)
        assert isinstance(value, str)
        assert value != "A realistic {interest_type} could be:"
        assert value != "Unknown Value"

def test_generate_user():
    user = generate_user()
    assert isinstance(user, dict)
    assert "name" in user
    assert "interests" in user
    assert isinstance(user["name"], str)
    assert isinstance(user["interests"], list)
    
    country_interest_count = 0
    for interest in user["interests"]:
        assert isinstance(interest, dict)
        assert "type" in interest
        assert "value" in interest
        assert "threshold" in interest
        assert isinstance(interest["type"], str)
        assert isinstance(interest["value"], str)
        assert isinstance(interest["threshold"], float)
        assert 0 <= interest["threshold"] <= 1
        
        if interest["type"] == "country":
            country_interest_count += 1
            assert interest["value"] in countries
    
    assert country_interest_count == 1

def test_generate_users():
    num_users = 10
    users = generate_users(num_users)
    assert isinstance(users, list)
    assert len(users) == num_users
    
    for user in users:
        assert isinstance(user, dict)
        assert "name" in user
        assert "interests" in user
        assert isinstance(user["name"], str)
        assert isinstance(user["interests"], list)

def test_save_to_json():
    users = generate_users(5)
    with open("./test_users.json", "w") as f:
        json.dump(users, f, indent=4)
    
    with open("./test_users.json", "r") as f:
        loaded_users = json.load(f)
    
    assert loaded_users == users
    
    # Clean up the generated file
    os.remove("./test_users.json")