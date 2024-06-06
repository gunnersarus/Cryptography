from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
from app import db
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random



class User:
    def __init__(self):
      self.check=""
    
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

      # Generate a base32 secret for 2FA
      #user['2fa_secret'] = pyotp.random_base32()

      if db.users.insert_one(user):
          return self.start_session(user)

      return jsonify({ "error": "Signup failed" }), 400

    def signout(self):
      session.clear()
      return redirect('/')

    def login(self):
      user = db.users.find_one({
          "email": request.form.get('email')
      })

      if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
          session['temp_user'] = user  # temporarily store user information for 2FA verification
          self.send_2fa_code(user['email'])
          return jsonify({"requires_2fa": True}), 200

      return jsonify({ "error": "Invalid login credentials" }), 401
    
   
    def send_2fa_code(self,email):
      # ... (giả sử bạn đã có biến otp chứa mã xác thực)
      otp=""
      for i in range(4):
       otp+=str(random.randint(0,9))
      session['2fa_otp'] = otp

      print(f"Generated OTP: {otp}")  # Debugging statement
      print(f"Stored check value: {self.check}")  # Debugging statement

      msg = MIMEText(otp)
      msg['Subject'] = 'Mã xác thực 2FA'
      msg['From'] = 'thanhptt1337@gmail.com'
      msg['To'] = ', '.join(["thanhptt1337@gmail.com", email])

      try:
          YOUR_EMAIL = "thanhptt1337@gmail.com"
          YOUR_PASSWORD = "ocipaivkplgoqsdk"

          with smtplib.SMTP('smtp.gmail.com', 587) as smtp_server:
              smtp_server.starttls()
              smtp_server.login(YOUR_EMAIL, YOUR_PASSWORD)
              smtp_server.send_message(msg)

          print("Email 2FA đã được gửi thành công!")  # In ra console log

        #  return jsonify({"status": "success", "message": "Mã 2FA đã được gửi"})
      except smtplib.SMTPException as e:
          error_msg = f'Lỗi gửi email: {str(e)}'
          print(error_msg)  # In ra console log khi có lỗi
          #return jsonify({"status": "error", "message": error_msg}), 500


    def verify_2fa(self, otpp):
        user = session.get('temp_user')
        if not user:
            return jsonify({"error": "Session expired, please login again"}), 400

        #totp = pyotp.TOTP(user['2fa_secret'])
        stored_otp = session.get('2fa_otp')
        print(f"OTP to verify: {otpp}")  # Debugging statement
        print(f"Stored OTP for verification: {stored_otp}")  # Debugging statement
        if(stored_otp==otpp):
            del session['temp_user']
            return self.start_session(user)
        
        print(f"day la otp moiw {stored_otp}")
        return jsonify({"error": "Invalid 2FA token"}), 401
    
  
  
