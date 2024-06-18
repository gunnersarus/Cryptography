from flask import Flask, request, session, redirect, render_template, Response,jsonify
from app import app
from models.decodeaudio_model import Audio
import os
import hashlib
import itertools
from flask import Flask, request, send_file

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/audio/decrypted')
def serve1audio():
    audio = Audio
    audio_buffer = Audio.get_cached_audio('piano.wav', 'piano.wav')
    if not audio_buffer:
        audio_buffer = Audio.get_audio('piano.wav', 'piano.wav')
    
    audio_buffer.seek(0)
    return send_file(audio_buffer, mimetype='audio/wav')


@app.route('/audio1/decrypted')
def serve2audio():
    audio = Audio
    audio_buffer = Audio.get_cached_audio('sample-file-4.wav', 'sample-file-4.wav')
    if not audio_buffer:
        audio_buffer = Audio.get_audio('sample-file-4.wav', 'sample-file-4.wav')
    
    audio_buffer.seek(0)
    return send_file(audio_buffer, mimetype='audio/wav')


@app.route('/audio2/decrypted')
def serve3audio():
    audio = Audio
    audio_buffer = Audio.get_cached_audio('sample-9s.wav', 'sample-9s.wav')
    if not audio_buffer:
        audio_buffer = Audio.get_audio('sample-9s.wav', 'sample-9s.wav')
    
    audio_buffer.seek(0)
    return send_file(audio_buffer, mimetype='audio/wav')
'''
decryptedsound.wav
'''
@app.route('/upload',methods = ["POST"])
def send():
    audio = Audio
    audio.send_audio('F:\\matma\\doan\\sample-9s.wav')
    #audio_buffer.seek(0)
    #eturn Response(audio_buffer.read(), mimetype='audio/wav')
    





@app.route('/upload', methods=['POST'])
def upload_file():
    audio =Audio
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    else:
        file_path = os.path.join('F:\\matma\\doan\\', file.filename)
        audio.send_audio(file_path)


    # Save the file to the upload folder
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    try:
        file.save(file_path)
        print(file_path)
        return jsonify({'message': 'File uploaded successfully', 'file_path': file_path})
    except Exception as e:
        return jsonify({'error': str(e)})

