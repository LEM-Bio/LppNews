import requests
import base64

# Set API endpoint and headers
headers = {"Authorization": "Client-ID 21f2a7a2fe66b70"}

# Read image file and encode as base64
def uploadImage(path):
    with open(path, "rb") as file:
        data = file.read()
        base64_data = base64.b64encode(data)

    # Upload image to Imgur and get URL
    url = "https://api.imgur.com/3/image"
    response = requests.post(url, headers=headers, data={"image": base64_data})
    url = response.json()["data"]["link"]
    return url
