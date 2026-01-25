#!/usr/bin/env python3
"""
Test der Chatbot API
"""
import requests
import json

API_URL = "http://localhost:8000/api/chatbot/message"

payload = {
    "message": "Hallo! Wie geht es dir?",
    "session_id": "test-session"
}

print(f"Sende Request zu {API_URL}...")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(API_URL, json=payload)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body:\n{response.text}")
    
except Exception as e:
    print(f"Fehler: {e}")
