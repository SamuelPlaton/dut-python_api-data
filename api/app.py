from flask import request, Flask
from flask_restplus import Api, Resource, fields
import json

app = Flask(__name__)
api = Api(app, version='1.0', title='ECI ADM/Devops demo API',
  description='Demo API',
)


# Route et fonction plus_one
@app.route('/plus_one/<int:x>')
@api.doc(params={'x': 'An Integer'})
class PlusOne(Resource):
  def get(self, x):
    x = int(x)
    return {x + 1}


# Route et fonction square 
@api.route('/square')
@api.doc(params={'x': 'An Integer'}, location='query')
class Square(Resource):
  def get(self):
    x = int(request.args.get('x', 1))
    return {x * x}

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int("5000"), debug=True)
