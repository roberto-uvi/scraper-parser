import requests

def extract_text(api_key, text_to_extract):
    url = "https://api.metatext.ai/v1/hub/inference/topic-analysis"
    headers = {
        'content-type': 'application/json',
        'x-api-key': api_key
    }
    data = {
        'text': text_to_extract
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code, response.text

api_key = 'rYox15E8qS4vYht3kiPYL4SuqdBCnoCN6TNP9Dur'  # Replace with your actual API key
text_to_extract = "LUXURY INCLUDEDÂ®CARIBBEAN RESORTS No other place in the world captures the imagination more than the Caribbean."

result = extract_text(api_key, text_to_extract)
print(result)