# app.py

from flask import Flask, render_template, request, url_for
from dotenv import load_dotenv
from datetime import datetime
from google_utils import upload_to_drive, get_shareable_link
import replicate
import os
import random
import requests
from openai import OpenAI


load_dotenv()
client = OpenAI()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        prompt = request.form.get('item')
        print(f'Added: {prompt}')

        messages = [{
            'role': 'user',
            'content': f'''
                {prompt}\n
                I want to generate a wallpaper image for this memory. 
                The image shouldn't have any intricate images or designs, 
                and more represent the general mood of the memory through 
                colors and shapes.
                
                Please return a prompt that I can pass to a diffusion 
                model to create such an image, briefly describing in one paragraph 
                how that image should look like. Return only the prompt.

                Start with the words 'Paint the fence with...'
            '''
            }]

        gpt_response = call_gpt(client, messages, "gpt-4-1106-preview")
        print(f'gpt_response: {gpt_response}')

        # Get a random mask filename
        mask_filename = get_random_mask()
        image_filename = get_image_path()
        print(f'mask_filename: {mask_filename}')
        print(f'image_filename: {image_filename}')

        # Upload files to Google Drive and get shareable links
        mask_file_id = upload_to_drive(os.path.basename(mask_filename), mask_filename, 'image/png')
        image_file_id = upload_to_drive(os.path.basename(image_filename), image_filename, 'image/png')

        mask_file_url = get_shareable_link(mask_file_id)
        image_file_url = get_shareable_link(image_file_id)
        
        print('mask_file_url', mask_file_url)
        print('image_file_url', image_file_url)

        background_path = os.path.join('static', 'background.jpg')

        output = replicate.run(
            "stability-ai/stable-diffusion-inpainting:c11bac58203367db93a3c552bd49a25a5418458ddffb7e90dae55780765e26d6",
            input={
                "mask": mask_file_url,
                "image": image_file_url,
                "width": 1024,
                "height": 768,
                "prompt": gpt_response,
                "scheduler": "DPMSolverMultistep",
                "num_outputs": 1,
                "guidance_scale": 7.5,
                "num_inference_steps": 25
            }
        )

        # Download the image from the Replicate API
        response = requests.get(output[0])

        if response.status_code == 200:
            # Save the downloaded image as the new background.jpg
            with open(background_path, 'wb') as f:
                f.write(response.content)
            # Save the downloaded image in the archive
            archive_folder = os.path.join('static', 'archive')
            archive_path = os.path.join(archive_folder, get_filename(prompt))
            with open(archive_path, 'wb') as f:
                f.write(response.content)
    return render_template('index.html')

def get_random_mask():
    mask_files = [file for file in os.listdir('static/masks/') if file.endswith('.jpg')]
    random_file = random.choice(mask_files)
    path = os.path.join('static/masks', random_file)
    return path

def get_image_path():
    # return os.path.join('static/archive', 'background_fence.jpg')
    return os.path.join('static', 'background.jpg')

def get_filename(prompt):
    timestamp = datetime.now().strftime("%d%m%y_%H%M%S_")
    return timestamp + prompt.replace(' ','')[:20] + '.jpg'

def call_gpt(client, messages, model):
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    return response.choices[0].message.content.strip()

if __name__ == '__main__':
    app.run()
