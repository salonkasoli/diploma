from flask import Flask, request, render_template, redirect, url_for
from db.postgre_connect import insert, select, Request
from convert import str_to_number, number_to_str

## here import stuff to cypher
from crypt.aes import get_cipher
from crypt.ope import get_ope_cipher
from crypt.pailier import get_he_cipher
from base64 import b64encode, b64decode
import binascii

app = Flask(__name__)

class Item():
    def __init__(self):
        pass

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
        is_effective = "yes"
    else:
        is_effective = "no"
    ciphered_name = str_to_number(det_encrypt_string(name))
    ciphered_age = ope_encrypt_int(age)
    ciphered_therapy_duration = ope_encrypt_int(therapy_duration)
    ciphered_gen_before = he_encrypt(gen_before_therapy)
    ciphered_gen_after = he_encrypt(gen_after_therapy)
    ciphered_is_effective = str_to_number(det_encrypt_string(is_effective))
    insert(ciphered_name, ciphered_age, ciphered_therapy_duration, ciphered_gen_before, ciphered_gen_after, ciphered_is_effective)
    return redirect(url_for('hello_world'))

@app.route('/q', methods=['POST'])    
def q():
    db_request = Request()
    name = request.form.get("name")
    age_min = request.form.get("age_min")
    age_max = request.form.get("age_max")
    therapy_duration_min = request.form.get("therapy_duration_min")
    therapy_duration_max = request.form.get("therapy_duration_max")
    is_effective = request.form.get("is_effective")
    if (name != None and len(name) > 0):
        db_request.name = str_to_number(det_encrypt_string(name))
    if (age_min != None and len(age_min) > 0):
        db_request.min_age = ope_encrypt_int(int(age_min))
    if (age_max != None and len(age_max) > 0):
        db_request.max_age = ope_encrypt_int(int(age_max))
    if (therapy_duration_min != None and len(therapy_duration_min) > 0):
        db_request.min_therapy_duration = ope_encrypt_int(int(therapy_duration_min))
    if (therapy_duration_max != None and len(therapy_duration_max) > 0):
        db_request.max_therapy_duration = ope_encrypt_int(int(therapy_duration_max))
    if (is_effective != None and len(is_effective) > 0):
        if (is_effective == 'yes' or is_effective == 'no'):
            db_request.is_effective = str_to_number(det_encrypt_string(is_effective))
    db_request.avg_gen_before = request.form.get("avg_before")
    db_request.avg_gen_after = request.form.get("avg_after")
    if (db_request.avg_gen_before != None or db_request.avg_gen_after != None):
        cipher = get_he_cipher()
        db_request.he_pub = cipher.pub.n
    rows = select(db_request)
    if (db_request.avg_gen_before != None or db_request.avg_gen_after != None):
        sum_before = None
        sum_after = None
        count = None
        count_index = 1
        if (db_request.avg_gen_before != None):
            sum_before = he_decrypt(int(rows[0][0]))
        if (db_request.avg_gen_after != None):
            after_index = 0
            if (db_request.avg_gen_before != None):
                after_index = 1
                count_index = 2
            sum_after = he_decrypt(int(rows[0][after_index]))
        count = rows[0][count_index]
        avg_before = None
        avg_after = None
        if (sum_before != None):
            avg_before = sum_before / count
        if (sum_after != None):
            avg_after = sum_after / count
        ## TODO redirect here to another page
        item = Item()
        item.count = count
        item.avg_before = avg_before
        item.avg_after = avg_after
        return render_template('average.html', item=item)
    items = []
    for row in rows:
        item = Item()
        item.name = det_decrypt_string(number_to_str(row[1]))
        item.age = ope_decrypt_int(int(row[2]))
        item.therapy_duration = ope_decrypt_int(int(row[3]))
        print 'gen before'
        print int(row[4])
        item.gen_before = he_decrypt(int(row[4]))
        item.gen_after = he_decrypt(int(row[5]))
        item.is_effective = det_decrypt_string(number_to_str(row[6]))
        items.append(item)
    return render_template('list.html', items=items)
    
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
    cipher = get_ope_cipher()
    return cipher.encrypt(value)
    
def ope_decrypt_int(value):
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
