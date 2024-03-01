import requests
import base64

#Code for forensic crymincal sketching

# Define the URL and the payload to send.
url = "http://127.0.0.1:7860"

payload = {
    "prompt": "An Asian woman in her 40s with light, smooth skin with oval face shape. Her hair is black and short, going down to her chin in a bob cut with dark eyebrows. Her hair swipes to the side across her short forehead. She has slanted eyes that are dark brown in color. Her nose is wide and round. She has thin lips and her ears are flat against her head. Her cheeks are filled out and her chin comes to rounded point. Suspect wears rectangular, black-framed glasses that have rounded corners.",
    "steps": 50
}

# Send said payload to said URL through the API.
response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
r = response.json()

print(r['images'][0])

#save the data to a text file
with open("output.txt", 'w') as f:
    f.write(r['images'][0])
    
# Decode and save the image.
with open("output.png", 'wb') as f:
    f.write(base64.b64decode(r['images'][0]))