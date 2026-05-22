import requests
import apikey

key = apikey.apikey

def test_connection(key, model="gpt-5.1"): 
    url = "https://llmproxy.uva.nl/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    body = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Hallo, dit is een test. Reageer met 'OK'."}
        ],
    }

    response = requests.post(url, headers=headers, json=body)
    print("Status:", response.status_code)
    print("Response:", response.json())

test_connection(key)