from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
from app import db,app
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import itertools
from wave import open as wave_open
import os
import io
from datetime import datetime,timedelta
import jwt

class User:
    def __init__(self):
      self.check=""

    def generatetoken(self,userid):
      payload={
          "id": userid,
            "expiration": str(datetime.utcnow()+ timedelta(seconds=120))
        }
      token = jwt.encode(
           payload= payload,
           key=app.secret_key,
           algorithm ='HS256'
        )
      return token 
    
    
    
    
    def start_session(self, user):
      del user['password']
      session.permanent= True
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
          "password": request.form.get('password'),
          "role": 'userr'
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

    def login(self):
      user = db.users.find_one({
          "email": request.form.get('email')
      })

      if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
          session['temp_user'] = user  # temporarily store user information for 2FA verification
          self.send_2fa_code(user['email'])
          return jsonify({"requires_2fa": True}), 200

      return jsonify({ "error": "Invalid login credentials" }), 401
    
    def send_2fa_code(self, email):
      otp = "".join([str(random.randint(0, 9)) for _ in range(4)])
      session['2fa_otp'] = otp

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

          print("Email 2FA đã được gửi thành công!")
      except smtplib.SMTPException as e:
          print(f'Lỗi gửi email: {str(e)}')

    def verify_2fa(self, otpp):
        user = session.get('temp_user')
        if not user:
            return jsonify({"error": "Session expired, please login again"}), 400

        stored_otp = session.get('2fa_otp')
        if stored_otp == otpp:
            session['token']= self.generatetoken(user["_id"])
            session['role']=user["role"]
            print(f'my role : {session['role']}')
            del session['temp_user']
            return self.start_session(user)
        
        return jsonify({"error": "Invalid 2FA token"}), 401

    def get_audio(self):
      big_num=2000
      collection_frame = db.frame
      collection_xor = db.xor

      def printlst(lst):
          print('[', lst[0], lst[1], lst[2], lst[3], lst[4], lst[5], '......', len(lst), "items ]")

      def keygen(x, r, size):
          key = []
          for i in range(size):
              x = r * x * (1 - x)
              key.append(((x * pow(10, 16)) % 256.126))
          return key

      print("Key generation:")
      a = 0.0125
      b = 3.9159
      printlst(keygen(a, b, big_num))

      print("Generate Deck keys using chaotic map")
      deckey = []
      for i in range(big_num):
          deckey.append(keygen(a, b, big_num)[i] - int(keygen(a, b, big_num)[i]))
      print(i + 1, "keys generated")
      print("Deck keys generated using chaotic map")
      printlst(deckey)

      print("Generate final keys from deck key")
      finkey = []
      for i in range(big_num):
          finkey.append(int(str(deckey[i])[-3:]))
      print("Final key generated:")
      printlst(finkey)

      print("Generate binary keys from final keys")
      binkey = []
      for i in range(big_num):
          binkey.append(bin(finkey[i]))
      print("Binary key generated:")
      printlst(binkey)

      print("Splitting binary keys on the 'b'")
      binkey_fin = []
      import re
      for i in range(big_num):
          binkey_fin.append(re.findall(r'\d+', binkey[i]))
      print("Now we have a list of lists:")
      printlst(binkey_fin)

      print("Converting list of lists into one list")
      merged = list(itertools.chain(*binkey_fin))
      print('The merged list is:')
      printlst(merged)
      print("Deleting the alternate zero values")
      del merged[0::2]
      print("After removing non-zero values we have")
      printlst(merged)
      print("Converting string to integer:")
      mergedfinal = list(map(int, merged))
      printlst(mergedfinal)

      xor_result = []
      document = collection_xor.find_one({"file_name": "piano.wav"})

      if document:
          text_data = document['text']
          xor_result = [int(line.strip()) for line in text_data.split('\n') if line.strip()]
          print("XOR Result:", xor_result)
      else:
          print("Document with file_name 'piano.wav' not found.")

      orig = []
      for i in range(len(xor_result)):
          xor = xor_result[i] ^ mergedfinal[i % len(mergedfinal)]
          orig.append(xor)

      print("The decrypted result is:")
      printlst(orig)

      checked = []
      print("Now converting them back into frames:")
      for num in orig:
          bytes_val = num.to_bytes(4, 'big')
          checked.append(bytes_val)
      printlst(checked)

      print("Now we write the values back into an audio file")
      audio_buffer = io.BytesIO()
      writer = wave_open(audio_buffer, 'wb')

      framelst1 = []
      document = collection_frame.find_one({"file_name": "piano.wav"})
      if document:
          text_data = document['text']
          framelst1 = [int(line.strip()) for line in text_data.split('\n') if line.strip()]
          print("Frame List:", framelst1)
      else:
          print("Document with file_name 'piano.wav' not found.")

      writer.setnchannels(framelst1[0])
      writer.setsampwidth(framelst1[1])
      writer.setframerate(framelst1[2])
      writer.setnframes(1)
      for frame in checked:
          writer.writeframesraw(frame)
      writer.close()

      audio_buffer.seek(0)
      return audio_buffer
