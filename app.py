from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome! Visit /bt for Big Tony bot"

@app.route('/bt')
def big_tony():
    return render_template('bt.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
