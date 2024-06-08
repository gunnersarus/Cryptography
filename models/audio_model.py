from flask import Flask
import itertools
from wave import open as wave_open
import io
import os
from app import db

class Audio:
    def get_audio():
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