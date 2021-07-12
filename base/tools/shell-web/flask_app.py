# Flask - Server
from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Code...
    return render_template('index.html')

app.run()