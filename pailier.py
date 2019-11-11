from paillier.paillier import *
import pickle

PAILLIER_PUB_KEY = "paillier_pub.txt"
PAILLIER_PRIVATE_KEY = "paillier_priv.txt"

def save(filename, key):
    f = open(filename, "w")
    pickle.dump(key, f)
    f.close()
    
def load(filename):
    try:
        f = open(filename, 'r')    
        pickle.load(f)
    except Exception:
        return None

def generate_key():
    priv, pub = generate_keypair(256)
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
    
    
priv, pub = get_key()
