from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
from app import db
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random


class User:

  def start_session(self, user):
    del user['password']
    session['logged_in'] = True
    session['user'] = user
    return jsonify(user), 200

  def signup(self):
    print(request.form)

    # Create the user object
    user = {
      "_id": uuid.uuid4().hex,
      "name": request.form.get('name'),
      "email": request.form.get('email'),
      "password": request.form.get('password')
    }

    # Encrypt the password
    user['password'] = pbkdf2_sha256.encrypt(user['password'])

    # Check for existing email address
    if db.users.find_one({ "email": user['email'] }):
      return jsonify({ "error": "Email address already in use" }), 400

    if db.users.insert_one(user):
      return self.start_session(user)

    return jsonify({ "error": "Signup failed" }), 400
  
  def signout(self):
    session.clear()
    return redirect('/')
  

  def send_2fa_code(self):
    # ... (giả sử bạn đã có biến otp chứa mã xác thực)
    otp=""
    for i in range(4):
     otp+=str(random.randint(0,9))

    msg = MIMEText(otp)
    msg['Subject'] = 'Mã xác thực 2FA'
    msg['From'] = 'thanhptt1337@gmail.com'
    msg['To'] = ', '.join(["thanhptt1337@gmail.com", "gklathumon@gmail.com"])

    try:
        YOUR_EMAIL = "thanhptt1337@gmail.com"
        YOUR_PASSWORD = "ocipaivkplgoqsdk"

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp_server:
            smtp_server.starttls()
            smtp_server.login(YOUR_EMAIL, YOUR_PASSWORD)
            smtp_server.send_message(msg)

        print("Email 2FA đã được gửi thành công!")  # In ra console log

        return jsonify({"status": "success", "message": "Mã 2FA đã được gửi"})
    except smtplib.SMTPException as e:
        error_msg = f'Lỗi gửi email: {str(e)}'
        print(error_msg)  # In ra console log khi có lỗi
        return jsonify({"status": "error", "message": error_msg}), 500
  
  
  def login(self):

    user = db.users.find_one({
      "email": request.form.get('email')
    })

    if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
      return self.send_2fa_code()
    
    return jsonify({ "error": "Invalid login credentials" }), 401