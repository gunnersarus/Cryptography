from flask import Flask, request, session, redirect, render_template
from app import app
from user.models import User

@app.route('/user/signup', methods=['POST'])
def signup():
    return User().signup()

@app.route('/user/signout')
def signout():
    return User().signout()

@app.route('/user/login', methods=['POST'])
def login():
    return User().login()

@app.route('/user/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    if request.method == 'POST':
        otp = request.form.get('otp')
        return User().verify_2fa(otp)
    return render_template('verify_2fa.html')
