from flask import Flask, request, render_template, redirect, url_for
from db.postgre_connect import insert, select, Request
from convert import str_to_number, number_to_str
from safedb import *

## here import stuff to cypher
from crypt.aes import get_cipher
from crypt.ope import get_ope_cipher
from crypt.pailier import get_he_cipher
from base64 import b64encode, b64decode
import binascii
import random
import string
import time

app = Flask(__name__)
request_builder = RequestBuilder()
request_builder.set_table_name("test_2")
request_builder.add_field("id", "none")
request_builder.add_field("name", "=")
request_builder.add_field("age", ">")
request_builder.add_field("therapy_duration", ">")
request_builder.add_field("gen_before", "+")
request_builder.add_field("gen_after", "+")
request_builder.add_field("is_effective", "=")

postgreRepository = PostgreRepository('test_1','ivan','localhost','qweasdzxc')

he_cipher = get_he_cipher()
ope_cipher = get_ope_cipher()
det_cipher = get_cipher()

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
    insertRequest = InsertRequest()
    insertRequest.addValue(request_builder.fields['name'], name)
    insertRequest.addValue(request_builder.fields['age'], age)
    insertRequest.addValue(request_builder.fields['therapy_duration'], therapy_duration)
    insertRequest.addValue(request_builder.fields['gen_before'], gen_before_therapy)
    insertRequest.addValue(request_builder.fields['gen_after'], gen_after_therapy)
    insertRequest.addValue(request_builder.fields['is_effective'], is_effective)
    
    print str(request_builder.build_insert_args(insertRequest))
    ciphered_name = str_to_number(det_encrypt_string(name))
    ciphered_age = ope_encrypt_int(age)
    ciphered_therapy_duration = ope_encrypt_int(therapy_duration)
    ciphered_gen_before = he_encrypt(gen_before_therapy)
    ciphered_gen_after = he_encrypt(gen_after_therapy)
    ciphered_is_effective = str_to_number(det_encrypt_string(is_effective))
    #insert(ciphered_name, ciphered_age, ciphered_therapy_duration, ciphered_gen_before, ciphered_gen_after, ciphered_is_effective)
    return redirect(url_for('hello_world'))

@app.route('/q', methods=['POST'])    
def q():
    db_request = Request()
    safe_request = SelectRequest()
    name = request.form.get("name")
    age_min = request.form.get("age_min")
    age_max = request.form.get("age_max")
    therapy_duration_min = request.form.get("therapy_duration_min")
    therapy_duration_max = request.form.get("therapy_duration_max")
    is_effective = request.form.get("is_effective")
    if (name != None and len(name) > 0):
        db_request.name = str_to_number(det_encrypt_string(name))
        safe_request.add_condition(request_builder.fields['name'],Condition("=", name))
    if (age_min != None and len(age_min) > 0):
        db_request.min_age = ope_encrypt_int(int(age_min))
        safe_request.add_condition(request_builder.fields['age'],Condition(">", age_min))
    if (age_max != None and len(age_max) > 0):
        db_request.max_age = ope_encrypt_int(int(age_max))
        safe_request.add_condition(request_builder.fields['age'],Condition("<", age_max))
    if (therapy_duration_min != None and len(therapy_duration_min) > 0):
        db_request.min_therapy_duration = ope_encrypt_int(int(therapy_duration_min))
        safe_request.add_condition(request_builder.fields["therapy_duration"] ,Condition(">", therapy_duration_min))
    if (therapy_duration_max != None and len(therapy_duration_max) > 0):
        db_request.max_therapy_duration = ope_encrypt_int(int(therapy_duration_max))
        safe_request.add_condition(request_builder.fields["therapy_duration"] ,Condition("<", therapy_duration_max))
    if (is_effective != None and len(is_effective) > 0):
        if (is_effective == 'yes' or is_effective == 'no'):
            db_request.is_effective = str_to_number(det_encrypt_string(is_effective))
            safe_request.add_condition(request_builder.fields["is_effective"],Condition("=", is_effective))
    db_request.avg_gen_before = request.form.get("avg_before")
    db_request.avg_gen_after = request.form.get("avg_after")
    if (db_request.avg_gen_before != None or db_request.avg_gen_after != None):
        cipher = get_he_cipher()
        db_request.he_pub = cipher.pub.n
        if (db_request.avg_gen_before != None):
            safe_request.add_avg_request(request_builder.fields["gen_before"])
        if (db_request.avg_gen_after != None):
            safe_request.add_avg_request(request_builder.fields["gen_after"])
    
    request_builder.build_select_request(safe_request)
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
    
@app.route('/fill', methods=['GET']) 
def fill_table():
    insert_test(100)
    insert_test(200)
    insert_test(300)
    insert_test(400)
    return redirect(url_for('hello_world'))
    
def insert_test(size):
    print 'insert test size ' + str(size)
    data = generate_data(size)
    clear_data = data[0]
    enc_data = data[1]
    clear_insert = 0
    ts = time.time()
    for clear in clear_data:
        insert(clear[0], clear[1], clear[2], clear[3], clear[4], clear[5], 'test_clear')
    clear_insert = (time.time() - ts)
    print 'clear inserted in  = ' + str(clear_insert)
        
    enc_insert = 0
    ts = time.time()
    for enc in enc_data:
        insert(enc[0], enc[1], enc[2], enc[3], enc[4], enc[5], 'test_2')
    enc_insert = (time.time() - ts)
    print 'enc inserted in  = ' + str(enc_insert)
    
@app.route('/test', methods=['GET']) 
def test():
    #select_ope_test(100)
    #select_ope_test(200)
    #select_ope_test(300)
    #select_ope_test(400)
    #select_ope_test(500)
    #select_ope_test(600)
    #select_ope_test(700)
    #select_ope_test(800)
    #select_ope_test(900)
    #select_ope_test(1000)
    #select_ope_test(1100)
    #select_ope_test(1200)
    #select_ope_test(1300)
    #select_ope_test(1400)
    #select_ope_test(1500)
    
    select_he_test(100)
    select_he_test(200)
    select_he_test(300)
    select_he_test(400)
    select_he_test(500)
    select_he_test(600)
    select_he_test(700)
    select_he_test(800)
    select_he_test(900)
    
    #select_det_test(100)
    #select_det_test(200)
    #select_det_test(400)
    #select_det_test(800)
    #select_det_test(1000)
    #select_det_test(1200)
    return redirect(url_for('hello_world'))
 
def select_ope_test(size):
    db_request = Request()
    clear_time = 0
    enc_time = 0
    decrypt_time = 0
    age = random_int(60)
    for i in range(size):
        age = 30
        db_request.max_age = age
        ts = time.time()
        rows_1 = select(db_request, "test_clear")
        clear_time += (time.time() - ts)
        encrypted = ope_encrypt_int(int(age))
        db_request.max_age = encrypted
        ts = time.time()
        rows_2 = select(db_request, "test_2")
        enc_time += (time.time() - ts)
        if len(rows_1) != len(rows_2):
            print "WTF. TESTS WRONG len 1 = " + str(len(rows_1)) + " len 2 = " + str(len(rows_2))
        else:
            pass
            #decrypt_time += decrypt(rows_2)
    print 'OPE select size = ' + str(size) + ' clear time = ' + str(clear_time) + " enc time = " + str(enc_time)
    #print 'Total decrypt time = ' + str(decrypt_time)
    
def select_det_test(size):
    db_request = Request()
    clear_time = 0
    enc_time = 0
    dec_time = 0
    for i in range(size):
        #name = random_string(10)
        name = 'khvduqqeot'
        db_request.name = name
        ts = time.time()
        rows_1 = select(db_request, "test_clear")
        clear_time += (time.time() - ts)
        ts = time.time()
        encrypted = str_to_number(det_encrypt_string(name))
        db_request.name = encrypted
        rows_2 = select(db_request, "test_2")
        enc_time += (time.time() - ts)
        if len(rows_1) != len(rows_2):
            print "WTF. TESTS WRONG len 1 = " + str(len(rows_1)) + " len 2 = " + str(len(rows_2))
        #if len(rows_1) > 0:
        #    print 'hooray!'
        dec_time += decrypt(rows_2)
    print 'DET select size = ' + str(size) + ' clear time = ' + str(clear_time) + " enc time = " + str(enc_time)
    print 'Decrypt time = ' + str(dec_time)
    
def select_he_test(size):
    db_request = Request()
    clear_time = 0
    enc_time = 0
    db_request.he_pub = he_cipher.pub.n
    for i in range(size):
        gen_before_therapy = random_int(1000)
        db_request.avg_gen_before = gen_before_therapy
        ts = time.time()
        rows_1 = select(db_request, "test_clear")
        clear_time += (time.time() - ts)
        #encrypted = he_encrypt(gen_before_therapy)
        db_request.avg_gen_before = gen_before_therapy
        ts = time.time()
        rows_2 = select(db_request, "test_2")
        sum_before = he_decrypt(int(rows_2[0][0])) / rows_2[0][1]
        enc_time += (time.time() - ts)
        if sum_before != rows_1[0][0]:
            pass
            #print "WTF. TESTS WRONG he sum = " + str(sum_before) + " actual = " + str(rows_1[0][0])
    print 'HE select times = ' + str(size) + ' clear time = ' + str(clear_time) + " enc time = " + str(enc_time)
    
def decrypt(rows):
    dec_time = 0
    ts = time.time()
    for row in rows:
        item = Item()
        item.name = det_decrypt_string(number_to_str(row[1]))
        item.age = ope_decrypt_int(int(row[2]))
        item.therapy_duration = ope_decrypt_int(int(row[3]))
        #print 'gen before'
        #print int(row[4])
        item.gen_before = he_decrypt(int(row[4]))
        item.gen_after = he_decrypt(int(row[5]))
        item.is_effective = det_decrypt_string(number_to_str(row[6]))
        #items.append(item)
    dec_time = time.time() - ts
    #print 'Decrypt time = ' + str(dec_time) + ' rows len = ' + str(len(rows))
    return dec_time

def generate_data(size):
    clear_data = []
    enc_data = []
    clear_time = 0
    enc_time = 0
    print 'generating data'
    for i in range(size):
        ts = time.time()
        name = random_string(10)
        age = random_int(60)
        therapy_duration = random_int(300)
        gen_before_therapy = random_int(1000)
        gen_after_therapy = random_int(1000)
        is_effective = random_string(10)
        clear_time += (time.time() - ts)
        clear_data.append((name, age, therapy_duration, gen_before_therapy, gen_after_therapy, is_effective))
        #insertRequest = InsertRequest()
        #insertRequest.addValue(request_builder.fields['name'], name)
        #insertRequest.addValue(request_builder.fields['age'], age)
        #insertRequest.addValue(request_builder.fields['therapy_duration'], therapy_duration)
        #insertRequest.addValue(request_builder.fields['gen_before'], gen_before_therapy)
        #insertRequest.addValue(request_builder.fields['gen_after'], gen_after_therapy)
        #insertRequest.addValue(request_builder.fields['is_effective'], is_effective)
        #print str(request_builder.build_insert_args(insertRequest))
        
        ts = time.time()
        ciphered_name = str_to_number(det_encrypt_string(name))
        ciphered_age = ope_encrypt_int(age)
        ciphered_therapy_duration = ope_encrypt_int(therapy_duration)
        ciphered_gen_before = he_encrypt(gen_before_therapy)
        ciphered_gen_after = he_encrypt(gen_after_therapy)
        ciphered_is_effective = str_to_number(det_encrypt_string(is_effective))
        enc_time += (time.time() - ts)
        enc_data.append((ciphered_name, ciphered_age, ciphered_therapy_duration, ciphered_gen_before, ciphered_gen_after, ciphered_is_effective))
    print 'all generated clear_time = ' + str(clear_time) + " enc_time = " + str(enc_time)
    return (clear_data, enc_data)
    
def random_string(strlen = 10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(strlen))
    
def random_int(max_int = 100):
    return random.randint(0,max_int)
    
    
def check_int(arg):
    if (arg == None):
        return 0
    if (len(arg) == 0):
        return 0
    return int(arg)
        
def det_encrypt_string(s):
    ct = get_cipher().encrypt(bytes(s))
    return b64encode(ct)
    
def det_decrypt_string(s):
    ct = b64decode(s)
    pt = get_cipher().decrypt(ct)
    return pt
    
def ope_encrypt_int(value):
    return ope_cipher.encrypt(value)
    
def ope_decrypt_int(value):
    return ope_cipher.decrypt(value)
    
def he_encrypt(value):
    return he_cipher.encrypt(value)

def he_decrypt(value):
    return he_cipher.decrypt(value)

if __name__ == '__main__':
    app.run()
