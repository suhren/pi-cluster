from flask import Flask
import platform

app = Flask(__name__)


@app.route('/')
def hello():
    return f'Hello World from {platform.uname()[1]}!'