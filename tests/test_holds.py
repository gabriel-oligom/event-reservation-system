import time
from datetime import datetime, timezone
import pytest

# ----- helpers -----
"""
These functions act as 'shortcuts' to avoid repeating code
"""

# Creates a new event with a given name and number of seats
def create_event(client, name="Test Event", total_seats=5):
    r = client.post("/events", json={"name": name, "total_seats": total_seats})
    assert r.status_code == 201, f"create_event failed: {r.status_code} {r.text}"
    return r.json()


# Retrieves all seats for a specific event
def get_seats(client, event_id):
    r = client.get(f"/events/{event_id}/seats")
    assert r.status_code == 200, f"get_seats failed: {r.status_code} {r.text}"
    return r.json()


# Places a temporary hold on a seat for a user
def post_hold(client, event_id, seat_id, user_id, seconds=60):
    r = client.post(f"/events/{event_id}/seats/{seat_id}/hold/", json={"user_id": user_id, "seconds": seconds})
    return r


# Refreshes an existing hold to extend its duration
def put_refresh_hold(client, event_id, seat_id, user_id, seconds=60):
    r = client.put(f"/events/{event_id}/seats/{seat_id}/hold/", json={"user_id": user_id, "seconds": seconds})
    return r


# Cancels a hold on a seat (only by the user who placed it)
def delete_hold(client, event_id, seat_id, user_id):
    r = client.delete(f"/events/{event_id}/seats/{seat_id}/hold/", json={"user_id": user_id})
    return r


# Attempts to reserve a seat for a user (requires active hold)
def post_reservation(client, event_id, seat_id, user_id):
    r = client.post(f"/events/{event_id}/seats/{seat_id}/reservation/", json={"user_id": user_id})
    return r


# ----- tests -----