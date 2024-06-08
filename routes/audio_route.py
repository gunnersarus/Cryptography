from flask import Flask, request, session, redirect, render_template, Response
from app import app
from models.audio_model import Audio

@app.route('/audio/decrypted')
def serve_audio():
    audio = Audio
    audio_buffer = audio.get_audio()
    audio_buffer.seek(0)
    return Response(audio_buffer.read(), mimetype='audio/wav')