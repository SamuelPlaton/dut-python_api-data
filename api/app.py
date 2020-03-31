from flask import request, Flask
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix

import json
import string
import csv # Nécessaire pour travailler sur des fichiers csv (nos datas)
import pandas as pd # pip3 install pandas
import spacy #pip3 install spacy ET python3 -m spacy download en_core_web_md

# Création de l'API, documentation minimale utile à Swagger.
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='ECI API',
  description='API de projet DEVOPS4 - ECI B1 Samuel Platon',
)

# Création d'un namespace, ajoute : 
# un namespace de routes /fct1 (localhost:5000/fct1) qui sera ensuite utilisé ensuite avec @ns.route
# création du namespace dans la documentation swagger
ns = api.namespace('fct1', description='Fonctionnalité 1 de l API')


# Déclaration d'un modèle de donnée utilisé dans l'API, il sert à :
# - Récupérer automatiquement des paramètres (vous le verrez dans la requête POST)
# - Générer les sorties de l'API (vous retournez une instance de ce modèle, elle est sérialisée pour vous en JSON automatiquement)
# - Documenter l'usage de ce modèle, les entrées et les sorties de l'API

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details')
})

# Déclaration d'une classe pour gérer les opérations CRUD (Create, Read, Update, Delete).
# Cette classe "fait le travail" et est appelée par les controllers de l'API. Ces derniers n'agissent pas directement sur les données. 

class TodoDAO(object):
    # Initialisation d'un compteur et d'une liste pour gérer les TODOs
    def __init__(self):
        self.counter = 0
        self.todos = []
    # Lecture d'un TODO par id (Appelé par /todo/1 par exemple, class TODO, verbe GET)
    def get(self, id):
        for todo in self.todos:
            if todo['id'] == id:
                return todo
        api.abort(404, "Todo {} doesn't exist".format(id))

    # Creation d'un TODO (voyez le paramètre data, et la façon dont il est transmis par la méthode post de la classe TodoList)
    def create(self, data):
        todo = data
        todo['id'] = self.counter = self.counter + 1
        self.todos.append(todo)
        return todo
    # Mise à jour d'un TODO
    def update(self, id, data):
        todo = self.get(id)
        todo.update(data)
        return todo
    # Suppression d'un TODO
    def delete(self, id):
        todo = self.get(id)
        self.todos.remove(todo)

# Route et fonction plus_one
@api.route('/plus_one/<x>')
@api.doc(params={'x': 'An Integer'})
class PlusOne(Resource):
  def get(self, x):
    x = int(x)
    return {"x": x + 1}


# Route et fonction square 
@api.route('/square/<x>')
@api.doc(params={'x': 'An Integer'})
class Square(Resource):
  def get(self, x):
    x = int(x)
    return {"x": x * x}

@api.route('/fct1')
class getDatas(Resource):

	def get(self):
		# On charge nos stopwords
		nlp = spacy.load("en_core_web_md") # charge le modèle en anglais
		spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
		# On récupère nos datas
		data = self.getData()
		# On effectue un prétraitement du texte
		data['Line'] = data.Line.apply( lambda phrase: self.pretraitement(phrase, nlp, spacy_stopwords) )
		return data[0:20].to_json()

	# On effectue un prétraitement de nos datas
	def pretraitement(self, phrase, nlp, spacy_stopwords):
		tokens = [ word.lemma_ for word in nlp(phrase) if word.text.lower() not in spacy_stopwords ]
		return ' '.join(tokens)

	# On récupère nos datas
	def getData(self):
		# On récupère tous nos dialogues dans nos fichiers .csv
		df1 = pd.read_csv('api/data/south-park/south-park-dialogues.csv')
		# On concatène tous les fichiers dans une variable
		data = pd.concat( [df1[0:20]] )
		data.sample(1)
		# On récupère seulement les personnages et les lignes de dialogue
		data = data[['Character','Line']].copy()
		# On retourne nos datas
		return data 	

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int("5000"), debug=True)

