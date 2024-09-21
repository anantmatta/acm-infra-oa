import os
import sqlite3
import pytest
from unittest.mock import patch
import uuid
from server import app


# Helper function to create a sample event data
def sample_event_data():
    return {
        "event_id": "abc123",
        "event_description": "Sample Event",
        "start_time": "2023-09-20T18:30:00Z",
        "capacity": 100,
        "price": 50.0,
        "sold": 10
    }


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture()
def setenvvar(monkeypatch):
    with patch.dict(os.environ, clear=True):
        envvars = {
            "DB_PATH": "data-testing.db",
        }
        for k, v in envvars.items():
            monkeypatch.setenv(k, v)
        yield


@patch('server.run_db_query')
def test_post_event(mock_run_db_query, client):
    """Test successful event creation."""
    # Prepare the mock
    mock_run_db_query.return_value = None

    # Sample data
    event_data = sample_event_data()

    # Send POST request
    response = client.post('/api/v1/events', json=event_data)

    # Validate response
    assert response.status_code == 201
    assert response.json['event_id'] == event_data['event_id']
    assert response.json['price'] == event_data['price']

    # Ensure the query was run
    assert mock_run_db_query.called

@patch('server.run_db_query')
def test_get_events(mock_run_db_query, client):
    """Test that the API successfully returns all events."""
    # Prepare the mock return value for the query
    mock_run_db_query.return_value.fetchall.return_value = [
        {
            'event_id': 'abc123',
            'event_description': 'Sample Event',
            'start_time': '2023-09-20T18:30:00Z',
            'capacity': 100,
            'price': 50.0,
            'sold': 10
        },
        {
            'event_id': 'def456',
            'event_description': 'Another Event',
            'start_time': '2023-09-22T18:30:00Z',
            'capacity': 200,
            'price': 75.0,
            'sold': 150
        },
        {
            'event_id': 'ghi789',
            'event_description': 'Another Event',
            'start_time': '2023-09-22T18:30:00Z',
            'capacity': 200,
            'price': 75.0,
            'sold': 200
        }
    ]

    # Send GET request
    response = client.get('/api/v1/events')

    # Validate response
    assert response.status_code == 200
    assert len(response.json) == 3
    assert response.json[0]['event_id'] == 'abc123'
    assert response.json[0]['tickets_left'] is True  # Capacity 100, sold 10, so tickets are available
    assert response.json[2]['event_id'] == 'ghi789'
    assert response.json[2]['tickets_left'] is False  # Capacity 200, sold 200, so no tickets are available

    # Ensure the query was run
    assert mock_run_db_query.called


@patch('server.run_db_query')
def test_get_events_no_data(mock_run_db_query, client):
    """Test when there are no events in the database."""
    # Prepare the mock to return an empty list
    mock_run_db_query.return_value.fetchall.return_value = []

    # Send GET request
    response = client.get('/api/v1/events')

    # Validate response
    assert response.status_code == 200
    assert len(response.json) == 0  # No events in the system

    # Ensure the query was run
    assert mock_run_db_query.called


@patch('server.run_db_query')
def test_get_events_error(mock_run_db_query, client):
    """Test when the database throws an error during GET."""
    # Mock to raise an error
    mock_run_db_query.side_effect = sqlite3.IntegrityError("Database Error")

    # Send GET request
    response = client.get('/api/v1/events')

    # Validate response
    assert response.status_code == 500
    assert response.json['error'] == "Could not read data. Please try again."

    # Ensure the query was run
    assert mock_run_db_query.called


@patch('server.run_db_query')
def test_post_event_db_error(mock_run_db_query, client):
    """Test when the database throws an error during POST."""
    # Mock to raise an error during insertion
    mock_run_db_query.side_effect = Exception("Database Error")

    # Sample data
    event_data = sample_event_data()

    # Send POST request
    response = client.post('/api/v1/events', json=event_data)

    # Validate response
    assert response.status_code == 500
    assert response.json['error'] == "Could not write data. Please check your request body."

    # Ensure the query was run
    assert mock_run_db_query.called


def test_create_and_get_event(setenvvar, client):
    """Test creating a new event and checking it in the DB (without mocking the DB)."""
    
    # Generate a random UUID for the event_id
    event_id = str(uuid.uuid4())
    
    # Sample data for a full event (sold == capacity)
    full_event_data = {
        "event_id": event_id,
        "event_description": "Full Event",
        "start_time": "2023-09-20T18:30:00Z",
        "capacity": 100,
        "price": 50.0,
        "sold": 100  # This makes the event "full"
    }

    # Create the full event
    post_response = client.post('/api/v1/events', json=full_event_data)

    # Check that the POST request succeeded
    assert post_response.status_code == 201
    assert post_response.json['event_id'] == event_id

    # Generate another random UUID for a not full event
    not_full_event_id = str(uuid.uuid4())
    
    # Sample data for a not-full event (sold < capacity)
    not_full_event_data = {
        "event_id": not_full_event_id,
        "event_description": "Not Full Event",
        "start_time": "2023-09-21T18:30:00Z",
        "capacity": 100,
        "price": 75.0,
        "sold": 50  # This makes the event "not full"
    }

    # Create the not-full event
    post_response = client.post('/api/v1/events', json=not_full_event_data)

    # Check that the POST request succeeded
    assert post_response.status_code == 201
    assert post_response.json['event_id'] == not_full_event_id

    # Send GET request to retrieve all events
    get_response = client.get('/api/v1/events')
    assert get_response.status_code == 200

    # Convert response JSON to a list
    events = get_response.json

    # Check that the "full event" is present and marked as full
    full_event = next(event for event in events if event['event_id'] == event_id)
    assert full_event['event_id'] == event_id
    assert full_event['tickets_left'] is False  # Full event should have no tickets left

    # Check that the "not full event" is present and marked as not full
    not_full_event = next(event for event in events if event['event_id'] == not_full_event_id)
    assert not_full_event['event_id'] == not_full_event_id
    assert not_full_event['tickets_left'] is True  # Not full event should have tickets left


## OPTIMAL PRICING tests

@patch('server.run_db_query')
def test_optimal_pricing_full_capacity(mock_run_db_query, client):
    """Test for event with no available capacity (fully booked)."""
    mock_run_db_query.return_value.fetchone.return_value = {'capacity': 50, 'sold': 50}

    # Mock request body with prices
    request_body = {'prices': [20, 30, 40, 50, 60]}

    response = client.post('/api/v1/events/fa24_full_event/optimal-pricing', json=request_body)

    # Check response
    assert response.status_code == 200
    assert response.json == {"optimal_price": -1, "tickets_sold": 0, "max_profit": 0}
    mock_run_db_query.assert_called_once()

@patch('server.run_db_query')
def test_optimal_pricing_enough_1(mock_run_db_query, client):
    """Test for event with enough capcity for all price candidiates."""
    mock_run_db_query.return_value.fetchone.return_value = {'capacity': 65, 'sold': 5}

    # Mock request body with prices
    request_body = {'prices': [20, 30, 40, 50]}

    response = client.post('/api/v1/events/fa24_barn_dance/optimal-pricing', json=request_body)

    # Check response
    assert response.status_code == 200
    assert response.json == {"optimal_price": 30, "tickets_sold": 3, "max_profit": 90}
    mock_run_db_query.assert_called_once()


@patch('server.run_db_query')
def test_optimal_pricing_enough_2(mock_run_db_query, client):
    """Test for event with enough capcity for all prices candidiates (with an obvious solution)."""
    mock_run_db_query.return_value.fetchone.return_value = {'capacity': 65, 'sold': 5}

    # Mock request body with prices
    request_body = {'prices': [20, 30, 40, 999999999]}

    response = client.post('/api/v1/events/fa24_barn_dance/optimal-pricing', json=request_body)

    # Check response
    assert response.status_code == 200
    assert response.json == {"optimal_price": 999999999, "tickets_sold": 1, "max_profit": 999999999}
    mock_run_db_query.assert_called_once()


@patch('server.run_db_query')
def test_optimal_pricing_enough_3(mock_run_db_query, client):
    """Test giving everybody tickets if no one is willing to pay for the event."""
    mock_run_db_query.return_value.fetchone.return_value = {'capacity': 65, 'sold': 5}

    # Mock request body with prices
    request_body = {'prices': [0, 0, 0]}

    response = client.post('/api/v1/events/fa24_barn_dance/optimal-pricing', json=request_body)

    # Check response
    assert response.status_code == 200
    assert response.json == {"optimal_price": 0, "tickets_sold": 3, "max_profit": 0}
    mock_run_db_query.assert_called_once()


@patch('server.run_db_query')
def test_optimal_pricing_enough_partial_1(mock_run_db_query, client):
    """Test only selling partial tickets if we don't have enough capacity."""
    mock_run_db_query.return_value.fetchone.return_value = {'capacity': 65, 'sold': 63}

    # Mock request body with prices
    request_body = {'prices': [99999, 99998, 99997]}

    response = client.post('/api/v1/events/fa24_barn_dance/optimal-pricing', json=request_body)

    # Check response
    assert response.status_code == 200
    assert response.json == {"optimal_price": 99998, "tickets_sold": 2, "max_profit": 199996}
    mock_run_db_query.assert_called_once()

@patch('server.run_db_query')
def test_optimal_pricing_invalid_capacity(mock_run_db_query, client):
    """Test for event with invalid capacity (0 capacity)."""
    mock_run_db_query.return_value.fetchone.return_value = {'capacity': 0, 'sold': 0}

    # Mock request body with prices
    request_body = {'prices': [20, 30, 40]}

    response = client.post('/api/v1/events/fa24_invalid_capacity/optimal-pricing', json=request_body)

    # Check response
    assert response.status_code == 200
    assert response.json == {"optimal_price": -1, "tickets_sold": 0, "max_profit": 0}
    mock_run_db_query.assert_called_once()

@patch('server.run_db_query')
def test_optimal_pricing_db_error(mock_run_db_query, client):
    """Test when the database throws an error."""
    mock_run_db_query.side_effect = Exception("Database Error")

    # Mock request body
    request_body = {'prices': [20, 30, 40]}

    response = client.post('/api/v1/events/fa24_semiformal/optimal-pricing', json=request_body)

    # Check response
    assert response.status_code == 500
    assert response.json == {"error": "Could not compute data. Please check your request body."}
    mock_run_db_query.assert_called_once()

@patch('server.run_db_query')
def test_optimal_pricing_complex_case(mock_run_db_query, client):
    """Test optimal pricing with multiple prices, capacity limits, and tie-breaking logic."""
    mock_run_db_query.return_value.fetchone.return_value = {'capacity': 100, 'sold': 80}

    # 30 prices with ties at two 150 values.
    request_body = {
        'prices': [90, 20, 30, 40, 50, 60, 70, 80, 90, 100,
                   110, 120, 130, 140, 150, 150, 160, 170, 180, 190, 200,
                   210, 220, 230, 240, 250, 260, 270, 280, 290, 300]
    }
    response = client.post('/api/v1/events/fa24_semiformal/optimal-pricing', json=request_body)
    
    assert response.status_code == 200
    assert response.json == {
        "optimal_price": 150,
        "tickets_sold": 17,
        "max_profit": 2550
    }
    mock_run_db_query.assert_called_once()
