from flask import Flask, request, render_template, redirect, url_for
from db.postgre_connect import insert
from convert import str_to_number
app = Flask(__name__)

@app.route('/')
def hello_world():
   return render_template('hello.html')
   
@app.route('/input')
def input():
    return render_template('input.html')
    
@app.route('/save', methods=['POST'])
def save():
    name = request.form.get('name')
    if (name == None or len(name) == 0):
        name = 'empty'
    name = str_to_number(name)
    age = check_int(request.form.get('age'))
    therapy_duration = check_int(request.form.get('therapy_duration'))
    gen_before_therapy = check_int(request.form.get('gen_before_therapy'))
    gen_after_therapy = check_int(request.form.get('gen_after_therapy'))
    is_effective = request.form.get('is_effective')
    if (is_effective != None):
        is_effective = 1
    else:
        is_effective = 0
    print is_effective
    print type(is_effective)
    insert(name, age, therapy_duration, gen_before_therapy, gen_after_therapy, is_effective)
    return redirect(url_for('hello_world'))
    
def check_int(arg):
    if (arg == None):
        return 0
    if (len(arg) == 0):
        return 0

if __name__ == '__main__':
   app.run()
