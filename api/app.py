from flask import request, Flask
import json

app = Flask(__name__)

# Route et fonction plus_one
@app.route('/plus_one/<int:x>')
def plus_one(x):
    return str(x+1)

# Route et fonction square 
@app.route('/square/<int:x>')
def square(x):
    return str(x*x)

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int("5000"), debug=True)
