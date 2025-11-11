import requests
import json

API_URL = "http://127.0.0.1:8000/process-query"

def test_query(query):
    try:
        payload = {"query": query}
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"{query}")
            print(f"Matched Intent: {data.get('intent_key', 'N/A')}")
            print(json.dumps(data, indent=2))
        else:
            print(f"Query: {query}")
            print(f"Error: {response.status_code}")
            print(f"Details: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server.")

if __name__ == "__main__":
    print("Type your query, or 'exit' to quit.")
    
    while True:
        user_input = input("\nEnter query: ")
        if user_input.lower() == 'exit':
            break
        
        if user_input:
            test_query(user_input)