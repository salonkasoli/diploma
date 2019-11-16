from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def hello_world():
   return "Hello world"
   
@app.route('/q')
def search():
    name = request.args.get("name")
    print name
    return str(name)

if __name__ == '__main__':
   app.run()
