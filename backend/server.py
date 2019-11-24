from flask import Flask, request, render_template, redirect, url_for
from db.postgre_connect import insert
from convert import str_to_number

## here import stuff to cypher
from crypt.aes import get_cipher
from crypt.ope import get_ope_cipher
from crypt.pailier import get_he_cipher
from base64 import b64encode, b64decode
import binascii

app = Flask(__name__)

@app.route('/')
def hello_world():
   return render_template('hello.html')
   
@app.route('/input')
def input():
    return render_template('input.html')
    
@app.route('/search')
def search():
    return render_template('search.html')
    
@app.route('/save', methods=['POST'])
def save():
    name = request.form.get('name')
    if (name == None or len(name) == 0):
        name = 'empty'
    age = check_int(request.form.get('age'))
    therapy_duration = check_int(request.form.get('therapy_duration'))
    gen_before_therapy = check_int(request.form.get('gen_before_therapy'))
    gen_after_therapy = check_int(request.form.get('gen_after_therapy'))
    is_effective = request.form.get('is_effective')
    if (is_effective != None):
        is_effective = "true"
    else:
        is_effective = "false"
    #convert it to num
    ciphered_name = det_encrypt_string(name)
    ciphered_age = ope_encrypt_int(age)
    ciphered_therapy_duration = ope_encrypt_int(therapy_duration)
    ciphered_gen_before = he_encrypt(gen_before_therapy)
    ciphered_gen_after = he_encrypt(gen_after_therapy)
    ciphered_is_effective = det_encrypt_string(is_effective)
    #insert(name, age, therapy_duration, gen_before_therapy, gen_after_therapy, is_effective)
    return redirect(url_for('hello_world'))
    
def check_int(arg):
    if (arg == None):
        return 0
    if (len(arg) == 0):
        return 0
    return int(arg)
        
def det_encrypt_string(s):
    cipher = get_cipher()
    ct = cipher.encrypt(bytes(s))
    return b64encode(ct)
    
def det_decrypt_string(s):
    ct = b64decode(s)
    cipher = get_cipher()
    pt = cipher.decrypt(ct)
    return pt
    
def ope_encrypt_int(value):
    print str(value)
    cipher = get_ope_cipher()
    return cipher.encrypt(value)
    
def ope_decrypt_int(value):
    print str(value)
    cipher = get_ope_cipher()
    return cipher.decrypt(value)
    
def he_encrypt(value):
    cipher = get_he_cipher()
    return cipher.encrypt(value)

def he_decrypt(value):
    cipher = get_he_cipher()
    return cipher.decrypt(value)

if __name__ == '__main__':
   app.run()
