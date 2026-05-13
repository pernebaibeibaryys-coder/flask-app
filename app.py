from flask import Flask, request, render_template, redirect, jsonify, send_from_directory
import numpy as np
import os
import socket
import requests
import cv2
from html.parser import HTMLParser
from contour_detection import detect_contours
from cryptography.fernet import Fernet
import base64
import hashlib

app = Flask(__name__)

# ❌ TensorFlow алып тасталды
hierarchy_score = 0.75

app.config['UPLOAD_FOLDER'] = 'uploads/'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists('static'):
    os.makedirs('static')


# =========================
# ENCRYPT FUNCTIONS
# =========================

def caesar_encrypt(text, shift):
    result = ''
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result

def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)

def aes_encrypt(text, key):
    key_hash = hashlib.sha256(key.encode()).digest()
    f_key = base64.urlsafe_b64encode(key_hash)
    f = Fernet(f_key)
    return f.encrypt(text.encode()).decode()

def aes_decrypt(text, key):
    key_hash = hashlib.sha256(key.encode()).digest()
    f_key = base64.urlsafe_b64encode(key_hash)
    f = Fernet(f_key)
    return f.decrypt(text.encode()).decode()

def base64_encrypt(text):
    return base64.b64encode(text.encode()).decode()

def base64_decrypt(text):
    return base64.b64decode(text.encode()).decode()


# =========================
# ROUTES
# =========================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    contours = detect_contours(file_path)
    num_contours = len(contours)

    img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    h, w = img.shape[:2]
    total_pixels = h * w

    density = round(num_contours / total_pixels, 10)
    alignment = round((num_contours * 2) / total_pixels, 10)
    visual = round((num_contours * 3.5) / total_pixels, 10)

    # ❌ TensorFlow орнына fake score
    hierarchy_score = 0.75
    prognoz = 1 if hierarchy_score > 0.5 else 0

    return render_template(
        'result.html',
        hierarchy_score=hierarchy_score,
        density=density,
        alignment=alignment,
        visual=visual,
        prognoz=prognoz,
        original_image=file.filename,
        processed_image='static/contours_detected.png'
    )


@app.route('/analyze_url', methods=['POST'])
def analyze_url():
    url = request.form.get('url', '')

    if not url:
        return jsonify({'error': 'URL не указан'})

    try:
        if not url.startswith('http'):
            url = 'https://' + url

        response = requests.get(url, timeout=10)

        domain = url.split('/')[2]
        ip = socket.gethostbyname(domain)

        try:
            geo = requests.get(f'https://ipapi.co/{ip}/json/', timeout=5).json()
            country = geo.get('country_name', 'Unknown')
        except:
            country = 'Unknown'

        return jsonify({
            'url': url,
            'country': country,
            'ip': ip,
            'status': response.status_code
        })

    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/encrypt', methods=['POST'])
def encrypt():
    text = request.form.get('text', '')
    method = request.form.get('method', '')
    key = request.form.get('key', '')

    try:
        if method == 'caesar':
            shift = int(key) if key.isdigit() else 3
            encrypted = caesar_encrypt(text, shift)
            decrypted = caesar_decrypt(encrypted, shift)

        elif method == 'aes':
            if not key:
                key = 'default_key'
            encrypted = aes_encrypt(text, key)
            decrypted = aes_decrypt(encrypted, key)

        elif method == 'base64':
            encrypted = base64_encrypt(text)
            decrypted = base64_decrypt(encrypted)

        else:
            return jsonify({'error': 'Метод не выбран'})

        return jsonify({
            'original': text,
            'encrypted': encrypted,
            'decrypted': decrypted
        })

    except Exception as e:
        return jsonify({'error': str(e)})


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
