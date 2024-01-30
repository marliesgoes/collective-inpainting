# app.py

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        item = request.form.get('item')
        print(f'Added: {item}')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
