import sys

from flask import Flask, render_template
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['STATIC_URL_PATH'] = '/static'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/page1')
def querys():
    return render_template('page1.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
