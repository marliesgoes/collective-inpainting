# app.py

from flask import Flask, render_template, request, url_for
from dotenv import load_dotenv
from datetime import datetime
from google_utils import upload_to_drive, get_shareable_link
from image_utils import merge_images
import replicate
import os
import random
import requests
import shutil
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
            '''
            }]

        gpt_response = call_gpt(client, messages, "gpt-4-1106-preview")
        print(f'gpt_response: {gpt_response}')

        prev_image = get_image_path()
        prev_image_id = upload_to_drive(os.path.basename(prev_image), prev_image, 'image/png')
        prev_image_url = get_shareable_link(prev_image_id)

        output = replicate.run(
            "stability-ai/stable-diffusion-img2img:15a3689ee13b0d2616e98820eca31d4c3abcd36672df6afce5cb6feb1d66087d",
            input={
                "image": prev_image_url,
                "prompt": gpt_response,
                "width": 1024,
                "height": 768,
                "num_outputs": 1,
                "guidance_scale": 9,
                "prompt_strength": 0.99,
                "num_inference_steps": 10
            }
        )

        # Download the image from the Replicate API
        response = requests.get(output[0])

        # Write plain result to archive
        archive_folder = os.path.join('static', 'archive')
        archive_path_raw = os.path.join(archive_folder, get_filename('raw_' + prompt))
        if response.status_code == 200:
            # Save the downloaded image as prev_image
            with open(archive_path_raw, 'wb') as f:
                f.write(response.content)

        mask_filename = get_mask_path()

        # Merge results and write to archive and background
        background_path = os.path.join('static', 'background.jpg')
        merge_images(background_path, archive_path_raw, mask_filename, background_path)
        archive_path_merged = os.path.join(archive_folder, get_filename('merged_' + prompt))
        shutil.copy(background_path, archive_path_merged)
        # update prev_image
        shutil.copy(archive_path_raw, prev_image)

    return render_template('index.html')

def get_mask_path():
    mask_files = [file for file in os.listdir('static/masks/') if file.endswith('.jpg')]
    random_file = random.choice(mask_files)
    path = os.path.join('static/masks', random_file)
    return path

def get_image_path():
    # return os.path.join('static/archive', 'background_fence.jpg')
    return os.path.join('static', 'prev_image.jpg')

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
