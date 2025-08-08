# Sample Flask app
from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
    return 'Hello from Gateway Appraisal v2.5'