import requests
import core.apikey as apikey

api_key = apikey.apikey # saved in a separate file for security reasons

def get_completions(model="gpt-4.1", system="", user="", key=api_key):
    url = "https://llmproxy.uva.nl/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": model,
        "messages": [{
            "role": "system",
            "content": f"{system}" 
        },
        {
            "role": "user",
            "content": f"{user}"
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=body)

        status_code = response.status_code

        if response.ok:
            data = response.json()
            completion = data["choices"][0]["message"]["content"]

            return completion, status_code

        else:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown error")
            
            return f"Error {status_code}: {error_message}", status_code
        
    except requests.exceptions.RequestException as e:
        return f"Request Exception: {str(e)}", 500

#completion = get_completions(model="gpt-5", system=system, user=user, key=apikey) # called in a different script, just for illsutration purposes
