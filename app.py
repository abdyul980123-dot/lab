from flask import Flask, render_template, send_from_directory
import os

# Get the directory where this script is located
basedir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            template_folder=basedir,
            static_folder=basedir,
            static_url_path='')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(basedir, filename)

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
