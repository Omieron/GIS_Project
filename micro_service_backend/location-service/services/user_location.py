import requests

def get_user_current_location(user_ip: str):
    response = requests.get(f"http://ip-api.com/json/{user_ip}")
    data = response.json()
    return {
        "latitude": data.get("lat"),
        "longitude": data.get("lon")
    }
