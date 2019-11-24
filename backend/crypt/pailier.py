from paillier import paillier
import pickle

PAILLIER_PUB_KEY = "paillier_pub.txt"
PAILLIER_PRIVATE_KEY = "paillier_priv.txt"

class HECipher:
    def __init__(self, priv, pub):
        self.priv = priv
        self.pub = pub
        
    def encrypt(self, value):
        return paillier.encrypt(self.pub, value)
        
    def decrypt(self, value):
        return paillier.decrypt(self.priv, self.pub, value)

def save(filename, key):
    f = open(filename, "w")
    pickle.dump(key, f)
    f.close()
    
def load(filename):
    try:
        f = open(filename, 'r')    
        return pickle.load(f)
    except Exception:
        return None

def generate_key():
    priv, pub = paillier.generate_keypair(128)
    save(PAILLIER_PUB_KEY, pub)
    save(PAILLIER_PRIVATE_KEY, priv)
    return priv, pub

def get_key():
    priv = load(PAILLIER_PRIVATE_KEY)
    if priv == None:
        return generate_key()
    pub = load(PAILLIER_PUB_KEY)
    if pub == None:
        return generate_key()
    return priv, pub
    
def get_he_cipher():
    priv, pub = get_key()
    return HECipher(priv, pub)
    
    
if __name__ == '__main__':
    cipher = get_he_cipher()
    ct = cipher.encrypt(123)
    print str(ct)
    pt = cipher.decrypt(ct)
    print str(pt)
    
