from flask import Flask, render_template, session, redirect,request
from functools import wraps
import pymongo
import jwt
from datetime import datetime,timedelta


app = Flask(__name__)
app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'

# Database
client = pymongo.MongoClient("mongodb+srv://tuchikien1234:F1rst_clust3r@healsouldb.86hstae.mongodb.net/")
db = client.MMH
app.permanent_session_lifetime = timedelta(minutes=10)



#Verify token 
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = session.get('token')
        if not token:
            return redirect('/login/')
        try:
            payload = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return redirect('/login/')
        except jwt.InvalidTokenError:
            return redirect('/login/')
        
        return func(*args, **kwargs)
    return decorated

# Decorators
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')
    return wrap

# Routes
from routes import audio_route,user_routes

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login/')
def loginn():
    return render_template('login.html')

@app.route('/signup/')
def signupp():
    return render_template('home.html')

@app.route('/dashboard/')
@login_required
@token_required
def dashboard():
    return render_template('user-info.html')

@app.route('/audioplay/')
@login_required
@token_required
def audio():
    return render_template('audio-play.html')

@app.route('/sendaudio/')
@login_required
@token_required
def sendaudio():
    role=session.get('role')
    if role=="admin":
     print(f'my role {role}')
     return render_template('upload.html')
    else:
     return render_template('user.html')
    
