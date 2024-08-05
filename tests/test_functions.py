import json
import pytest
from unittest.mock import mock_open, patch

from helper_functions.helper_functions import load_data, match_country_content, match_country_and_content

@pytest.fixture
def mock_users_and_content():
    # Mock data for users and content
    users_data = json.dumps([{
        "name": "Alice",
        "interests": [{"type": "country", "value": "USA", "threshold": 0.5}]
    }])
    
    content_data = json.dumps([{
        "title": "Content 1",
        "tags": [{"type": "country", "value": "USA"}],
        "content": "This is content 1",
        "priority": 1
    }, {
        "title": "Content 2",
        "tags": [{"type": "country", "value": "Canada"}],
        "content": "This is content 2",
        "priority": 2
    }])
    
    return users_data, content_data

@patch('builtins.open', new_callable=mock_open)
def test_load_data(mock_file, mock_users_and_content):
    mock_file.side_effect = [
        mock_open(read_data=mock_users_and_content[0]).return_value,
        mock_open(read_data=mock_users_and_content[1]).return_value
    ]

    users, content = load_data()
    
    # Check if users and content are loaded correctly
    assert len(users) == 1
    assert users[0]['name'] == "Alice"
    assert len(content) == 2
    assert content[0]['title'] == "Content 1"

def test_match_country_content(mock_users_and_content):
    users = json.loads(mock_users_and_content[0])
    content = json.loads(mock_users_and_content[1])

    expected_output = {
        "Alice": [content[0]]  # Alice should match with Content 1
    }

    result = match_country_content(users, content)
    
    # Check if the matched content is correct
    assert result == expected_output

def test_no_matching_content():
    users = [
        {
            "name": "Bob",
            "interests": [{"type": "country", "value": "UK", "threshold": 0.5}]
        }
    ]
    content = [
        {
            "title": "Content 1",
            "tags": [{"type": "country", "value": "USA"}],
            "content": "This is content 1",
            "priority": 1
        }
    ]

    expected_output = {
        "Bob": []  # Bob should not match any content
    }

    result = match_country_content(users, content)
    
    # Check if the matched content is correct
    assert result == expected_output
    
def test_match_country_and_content():
    users = [
        {
            "name": "Alice",
            "interests": [
                {"type": "country", "value": "USA"},
                {"type": "topic", "value": "Technology"}
            ]
        },
        {
            "name": "Bob",
            "interests": [
                {"type": "country", "value": "Canada"},
                {"type": "topic", "value": "Health"}
            ]
        }
    ]

    content = [
        {
            "title": "Tech Innovations in USA",
            "tags": [
                {"type": "country", "value": "USA"},
                {"type": "topic", "value": "Technology"}
            ],
            "content": "This article discusses tech innovations in the USA."
        },
        {
            "title": "Health Tips for Canadians",
            "tags": [
                {"type": "country", "value": "Canada"},
                {"type": "topic", "value": "Health"}
            ],
            "content": "This article provides health tips for Canadians."
        },
        {
            "title": "Traveling to Canada",
            "tags": [
                {"type": "country", "value": "Canada"},
                {"type": "topic", "value": "Travel"}
            ],
            "content": "This article is about traveling to Canada."
        }
    ]

    expected_output = {
        "Alice": [
            {
                "title": "Tech Innovations in USA",
                "tags": [
                    {"type": "country", "value": "USA"},
                    {"type": "topic", "value": "Technology"}
                ],
                "content": "This article discusses tech innovations in the USA."
            }
        ],
        "Bob": [
            {
                "title": "Health Tips for Canadians",
                "tags": [
                    {"type": "country", "value": "Canada"},
                    {"type": "topic", "value": "Health"}
                ],
                "content": "This article provides health tips for Canadians."
            }
        ]
    }

    result = match_country_and_content(users, content)
    assert result == expected_output
    
# Test cases for the match_country_and_content function
def test_match_country_and_content():
    users = [
        {
            "name": "Alice",
            "interests": [
                {"type": "country", "value": "USA"},
                {"type": "topic", "value": "Technology"}
            ]
        },
        {
            "name": "Bob",
            "interests": [
                {"type": "country", "value": "Canada"},
                {"type": "topic", "value": "Health"}
            ]
        }
    ]

    content = [
        {
            "title": "Tech Innovations in USA",
            "tags": [
                {"type": "country", "value": "USA"},
                {"type": "topic", "value": "Technology"}
            ],
            "content": "This article discusses tech innovations in the USA."
        },
        {
            "title": "Health Tips for Canadians",
            "tags": [
                {"type": "country", "value": "Canada"},
                {"type": "topic", "value": "Health"}
            ],
            "content": "This article provides health tips for Canadians."
        },
        {
            "title": "Traveling to Canada",
            "tags": [
                {"type": "country", "value": "Canada"},
                {"type": "topic", "value": "Travel"}
            ],
            "content": "This article is about traveling to Canada."
        }
    ]

    expected_output = {
        "Alice": [
            {
                "title": "Tech Innovations in USA",
                "tags": [
                    {"type": "country", "value": "USA"},
                    {"type": "topic", "value": "Technology"}
                ],
                "content": "This article discusses tech innovations in the USA."
            }
        ],
        "Bob": [
            {
                "title": "Health Tips for Canadians",
                "tags": [
                    {"type": "country", "value": "Canada"},
                    {"type": "topic", "value": "Health"}
                ],
                "content": "This article provides health tips for Canadians."
            }
        ]
    }

    result = match_country_and_content(users, content)
    assert result == expected_output

def test_no_matching_content():
    users = [
        {
            "name": "Charlie",
            "interests": [
                {"type": "country", "value": "UK"},
                {"type": "topic", "value": "Sports"}
            ]
        }
    ]

    content = [
        {
            "title": "Tech Innovations in USA",
            "tags": [
                {"type": "country", "value": "USA"},
                {"type": "topic", "value": "Technology"}
            ],
            "content": "This article discusses tech innovations in the USA."
        }
    ]

    expected_output = {
        "Charlie": []  # No content should match Charlie's interests
    }

    result = match_country_and_content(users, content)
    assert result == expected_output

def test_multiple_users_with_exact_matches():
    users = [
        {
            "name": "Alice",
            "interests": [
                {"type": "country", "value": "USA"},
                {"type": "topic", "value": "Technology"}
            ]
        },
        {
            "name": "Bob",
            "interests": [
                {"type": "country", "value": "Canada"},
                {"type": "topic", "value": "Health"}
            ]
        }
    ]

    content = [
        {
            "title": "Tech Innovations in USA",
            "tags": [
                {"type": "country", "value": "USA"},
                {"type": "topic", "value": "Technology"}
            ],
            "content": "This article discusses tech innovations in the USA."
        },
        {
            "title": "Health Tips for Canadians",
            "tags": [
                {"type": "country", "value": "Canada"},
                {"type": "topic", "value": "Health"}
            ],
            "content": "This article provides health tips for Canadians."
        },
        {
            "title": "Traveling to Canada",
            "tags": [
                {"type": "country", "value": "Canada"},
                {"type": "topic", "value": "Travel"}
            ],
            "content": "This article is about traveling to Canada."
        }
    ]

    expected_output = {
        "Alice": [
            {
                "title": "Tech Innovations in USA",
                "tags": [
                    {"type": "country", "value": "USA"},
                    {"type": "topic", "value": "Technology"}
                ],
                "content": "This article discusses tech innovations in the USA."
            }
        ],
        "Bob": [
            {
                "title": "Health Tips for Canadians",
                "tags": [
                    {"type": "country", "value": "Canada"},
                    {"type": "topic", "value": "Health"}
                ],
                "content": "This article provides health tips for Canadians."
            }
        ]
    }

    result = match_country_and_content(users, content)
    assert result == expected_output

def test_no_country_or_other_interest_match():
    users = [
        {
            "name": "Alice",
            "interests": [
                {"type": "country", "value": "USA"},
                {"type": "topic", "value": "Health"}
            ]
        }
    ]

    content = [
        {
            "title": "Tech Innovations in Canada",
            "tags": [
                {"type": "country", "value": "Canada"},
                {"type": "topic", "value": "Technology"}
            ],
            "content": "This article discusses tech innovations in Canada."
        }
    ]

    expected_output = {
        "Alice": []  # No content should match Alice's interests
    }

    result = match_country_and_content(users, content)
    assert result == expected_output