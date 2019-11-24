import json
from base64 import b64encode
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from Crypto.Random import get_random_bytes
from serialize import *
from deserialize import *

AES_KEY_FILE = "aes_key.txt"

class DetCipher:
    def __init__(self, cipher):
        self.cipher = cipher
        
    def encrypt(self, data):
        ct_bytes = self.cipher.encrypt(pad(data, AES.block_size))
        return ct_bytes
        
    def decrypt(self, ct_bytes):
        pt = unpad(self.cipher.decrypt(ct_bytes), AES.block_size)
        return pt
        


def generate_key_info():
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC)
    encoded_iv = b64encode(cipher.iv).decode('utf-8')
    encoded_key = b64encode(key).decode('utf-8')
    key_info = str(json.dumps({'iv':encoded_iv, 'key':encoded_key}))
    save(AES_KEY_FILE, key_info)
    return key_info
    
def get_key_info():
    key_info = load(AES_KEY_FILE)
    if (key_info == None):
        key_info = generate_key_info()
    return key_info
        
def get_cipher():
    key_info = get_key_info()
    b64 = json.loads(key_info)
    iv = b64decode(b64['iv'])
    key = b64decode(b64['key'])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return DetCipher(cipher)
    
    
if __name__== "__main__":
    cipher = get_cipher()
    data = b'123'
    ct = cipher.encrypt(data)
    print ct
    cipher = get_cipher()
    pt = cipher.decrypt(ct)
    print data
