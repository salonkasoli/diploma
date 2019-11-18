from flask import Flask, request, render_template, redirect, url_for
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
    age = request.form.get('age')
    therapy_duration = request.form.get('therapy_duration')
    gen_before_therapy = request.form.get('gen_before_therapy')
    gen_after_therapy = request.form.get('gen_after_therapy')
    is_effective = request.form.get('is_effective')
    print str(is_effective != None)
    return redirect(url_for('hello_world'))

if __name__ == '__main__':
   app.run()
