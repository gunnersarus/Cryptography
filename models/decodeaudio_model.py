from flask import Flask
import itertools
from wave import open as wave_open
import io
import os
from app import db

class Audio:
    def get_audio(nameframe,namexor):
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
        document = collection_xor.find_one({"file_name": namexor})

        if document:
            text_data = document['text']
            xor_result = [int(line.strip()) for line in text_data.split('\n') if line.strip()]
            print("XOR Result:", xor_result)
        else:
            print(f"Document with file_name ${namexor} not found.")

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
        document = collection_frame.find_one({"file_name": nameframe})
        if document:
            text_data = document['text']
            framelst1 = [int(line.strip()) for line in text_data.split('\n') if line.strip()]
            print("Frame List:", framelst1)
        else:
            print(f"Document with file_name ${nameframe} not found.")

        writer.setnchannels(framelst1[0])
        writer.setsampwidth(framelst1[1])
        writer.setframerate(framelst1[2])
        writer.setnframes(1)
        for frame in checked:
            writer.writeframesraw(frame)
        writer.close()

        audio_buffer.seek(0)
        return audio_buffer
    
    def send_audio(audio_path):
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

        #import wave



       # wave_file_path = "D:\\MMHpro\\crypt\\Cryptography\\sound\\+ {audio_path}"
        wave_file_path = audio_path
        w = wave_open(wave_file_path, 'rb')
        # w= wave_open("D:\\MMH\\MMHproject\\MMH\\sound\\piano.wav",'rb')


        channels=w.getnchannels()
        print("Number of channels",channels)

        framerate=w.getframerate()
        print("FrameRate:",framerate)

        sampwidth=w.getsampwidth()
        print("Sample Width:",sampwidth)

        file_nameofpath = os.path.basename(wave_file_path)

        framelist =[]
        framelist.append(channels)
        framelist.append(sampwidth)
        framelist.append(framerate)
        # filename = 'frame-output.txt'
        # outfile = open("D:\\MMH\\MMHproject\\MMH\\"+filename, 'w')
        # outfile.writelines([str(i)+'\n' for i in framelist])
        # outfile.close()
        text_data = "\n".join([str(i) for i in framelist])
        audio_metadata = {
            "file_name": file_nameofpath,
            "text": text_data
        }

        # Insert data into MongoDB
        collection_frame.insert_one(audio_metadata)

        print("Audio metadata inserted into MongoDB successfully.")



        print("\nNumber of Frames: ", w.getnframes())
        frameslst=[]
        for i in range(w.getnframes()):
            frame=w.readframes(1)
            frameslst.append(frame)
            #print(frame)

        print("The frames are")
        printlst(frameslst)

        print("\nNow converting them into integers\n")
        intframe=[]
        for frame in frameslst :
            int_val = int.from_bytes(frame, "big")
            intframe.append(int_val)
            #print(int_val)

        print("The integer frames are:\n")
        printlst(intframe)

        keysize = len(mergedfinal)
        print("The number of key values we have generated :",keysize)

        print("The number of byte frames we have :",len(intframe))


        print("XOR - ENCRYPTION") 

        xor_result=[]

        for i in range(len(intframe)):
            xor=intframe[i]^mergedfinal[i%keysize] # m mod n returns a value only from 0 to n , no matter how large m is 
            xor_result.append(xor)

        print("The XOR result is:")
        printlst(xor_result)




        # filename = 'xor-result-output.txt'
        # outfile = open("D:\\MMH\\MMHproject\\MMH\\"+filename, 'w')
        # outfile.writelines([str(i)+'\n' for i in xor_result])
        # outfile.close()
        #Convert XOR Result to bytearray
        text_data = "\n".join([str(i) for i in xor_result])
        xor_metadata = {
            "file_name": file_nameofpath,
            "text": text_data
        }

        # Insert data into MongoDB
        collection_xor.insert_one(xor_metadata)

        print("XOR result data inserted into MongoDB successfully.")

        check=[]
        print("Now converting XOR values into frames:")
        for num in xor_result:
            bytes_val = num.to_bytes(4, 'big')
            #print(bytes_val)
            check.append(bytes_val)
        check.reverse()
        print("\nBytes list\n")
        printlst(check)

        #code to convert bytearray to wav audio file

        print("Now writing the encypted values to an audio file")
        inputfilename= os.path.basename(audio_path)
        filename='encrypted-'+ inputfilename

        
        writer=wave_open("F:\\matma\\doan\\"+filename,'wb')


        writer.setnchannels(channels)
        writer.setsampwidth(sampwidth)
        writer.setframerate(framerate)
        writer.setnframes(1)
        for frame in check:
            writer.writeframesraw(frame)
        writer.close()

        print("Written to file ", filename)
        print("uploaded")