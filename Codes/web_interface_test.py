from flask import Flask, render_template, request, redirect, url_for
import requests
import base64
import matplotlib.pyplot as plt
from openai import OpenAI
import os
from dotenv import load_dotenv

base64_img = {}

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form['prompt']

    delimiter = "####"
    system_message = f"""
    The input is a prompt for a forensic criminal sketching generative AI tool describing facial characteristics.
    If there is something like "almond eyes", "sunglasses", "crooked teeth" in the prompt, highlight those parts with round brackets.
    Send back the prompt with the refinements done for a better output from the generative tool as face information.
    Message will be delimited with {delimiter} characters.
    """

    input_user_message = prompt
    input_user_message = input_user_message.replace(delimiter, "")
    user_message_for_model = f"""User message, remember that your response to the user must be the required prompt to the criminal detection tool {delimiter}{input_user_message}{delimiter}"""

    refined_prompts = []

    chat_log = client.chat.completions.create(
        messages=[
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': user_message_for_model},
        ],
        model="gpt-3.5-turbo",
        max_tokens=50  # Adjust this value based on your desired maximum token limit
    )

    refined_prompt = chat_log.choices[0].message.content.replace('####', '')
    refined_prompts.append(refined_prompt)

    for i in range(3):
        
        # Define the payload to send for each image
        payload = {
            "positive_prompt": "photo, portrait, face, looking at viewer, plain background",
            "negative_prompt": "(((deformed face))),(side view:1.2), worst quality, low quality, low res, blurry, text, watermark, logo, banner, extra digits, cropped, jpeg artifacts, error, sketch ,duplicate, monochrome, geometry, mutation, fused face, cloned face",
            "prompt": refined_prompt,
            "steps": 10,
            "width": 512,
            "height": 512,
        }

        # Send payload to the API for each image
        response = requests.post(url=f'http://127.0.0.1:7860/sdapi/v1/txt2img', json=payload)
        r = response.json()

        base64_img[i] = r['images'][0]

        # Decode and save the image with a unique filename
        with open(f"static/output{i+1}.png", 'wb') as f:
            f.write(base64.b64decode(r['images'][0]))

    return render_template('index.html', refined_prompts=refined_prompts, base64_1=base64_img[0], base64_2=base64_img[1], base64_3=base64_img[2])

@app.route('/refine_gen', methods=['POST'])
def refine_gen():
    prompt = request.form['refinePrompt']

    # Read the image file and convert it to base64
    with open("target.png", "rb") as img_file:
        img_data = base64.b64encode(img_file.read()).decode('utf-8')

    for i in range(3):
        
        # Define the payload to send for each image
        payload = {
            "positive_prompt": "photo, portrait, face, looking at viewer, plain background",
            "negative_prompt": "(((deformed face))),(side view:1.2), worst quality, low quality, low res, blurry, text, watermark, logo, banner, extra digits, cropped, jpeg artifacts, error, sketch ,duplicate, monochrome, geometry, mutation, fused face, cloned face",
            "prompt": prompt,
            "steps": 10,
            "width": 512,
            "height": 512,
            "init_images": [
                img_data
            ]
        }

        # Send payload to the API for each image
        response = requests.post(url=f'http://127.0.0.1:7860/sdapi/v1/img2img', json=payload)
        r = response.json()

        base64_img[i] = r['images'][0]

        # Decode and save the image with a unique filename
        with open(f"static/output{i+1}.png", 'wb') as f:
            f.write(base64.b64decode(r['images'][0]))

    return render_template('index.html', refined_prompts=prompt, base64_1=base64_img[0], base64_2=base64_img[1], base64_3=base64_img[2])


@app.route('/refine', methods=['POST'])
def refine():
    image_number = request.form.get('image_number')
    
    # Assuming you want to save the output image as 'target.png'
    target_filename = 'target.png'
    base64_image = base64_img[int(image_number) - 1]

    # Decode and save the image with the specified filename
    with open(target_filename, 'wb') as f:
        f.write(base64.b64decode(base64_image))

    return render_template('image_refiner.html', image_number=image_number)

if __name__ == '__main__':
    app.run(debug=True)
