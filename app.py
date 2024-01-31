# app.py

from flask import Flask, render_template, request, url_for
from dotenv import load_dotenv
from datetime import datetime
import replicate
import os
import random
import requests

load_dotenv()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        item = request.form.get('item')
        print(f'Added: {item}')

        # Get a random mask filename
        hostname = request.host_url.rstrip('/')
        mask_filename = get_random_mask(hostname)
        image_filename = get_image_path(hostname)

        print('mask_filename', mask_filename)
        print('image_filename', image_filename)

        background_path = os.path.join('static', 'background.jpg')

        output = replicate.run(
            "stability-ai/stable-diffusion-inpainting:c11bac58203367db93a3c552bd49a25a5418458ddffb7e90dae55780765e26d6",
            input={
                "mask": mask_filename,
                "image": image_filename,
                "width": 512,
                "height": 512,
                "prompt": item,
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
            archive_path = os.path.join(archive_folder, get_filename())
            with open(archive_path, 'wb') as f:
                f.write(response.content)
    return render_template('index.html')

def get_random_mask(hostname):
    mask_files = os.listdir('static/masks/')
    random_file = random.choice(mask_files)
    path = os.path.join(hostname, 'static/masks')
    return os.path.join(path, random_file)

def get_image_path(hostname):
    url = url_for('static', filename='background.jpg')
    return hostname + url

def get_filename():
    return datetime.now().strftime("%d%m%y_%H%M%S.jpg")

if __name__ == '__main__':
    app.run()
