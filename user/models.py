from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
from app import db
import uuid
import pyotp

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

      # Generate a base32 secret for 2FA
      user['2fa_secret'] = pyotp.random_base32()

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
          return jsonify({"requires_2fa": True}), 200

      return jsonify({ "error": "Invalid login credentials" }), 401


    def verify_2fa(self, otp):
        user = session.get('temp_user')
        if not user:
            return jsonify({"error": "Session expired, please login again"}), 400

        totp = pyotp.TOTP(user['2fa_secret'])
        if totp.verify(otp):
            del session['temp_user']
            return self.start_session(user)
        
        return jsonify({"error": "Invalid 2FA token"}), 401
