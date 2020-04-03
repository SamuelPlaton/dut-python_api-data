from flask import request, Flask, jsonify
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix

import json
import string
import csv # Nécessaire pour travailler sur des fichiers csv (nos datas)
import pandas as pd # pip3 install pandas
import spacy #pip3 install spacy ET python3 -m spacy download en_core_web_md
import nltk #pip3 install nltk
from flask_swagger import swagger

# Création de l'API, documentation minimale utile à Swagger.
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='ECI API',
  description='API de projet DEVOPS4 - ECI B1 Samuel Platon',
)

# Création d'un namespace, ajoute : 
# un namespace de routes /fct1 (localhost:5000/fct1) qui sera ensuite utilisé ensuite avec @ns.route
# création du namespace dans la documentation swagger
ns1 = api.namespace('/vocabulary/<c>', description='Fonctionnalité 1 de l API')


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

# Get the swagger doc
@api.route('/spec')
class getSpec(Resource):
	def get(self):
		swag = swagger(app)
		# Informations about the API
		swag['info']['version'] = "1.0"
		swag['info']['title'] = "Samuel Platon - ECIB1 - My API"
		# Informations about functionnalities
		swag['info']['functionnality 1'] = " Return the vocabulary of a specific character"
		return jsonify(swag)

# Retrieve and pretreat data
class getDatas(Resource):
	def get(self):
		# Loading our stopwords
		nlp = spacy.load("en_core_web_md") # loading the english model
		spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
		# Getting back our datas
		data = self.getData()
		# Pretreatment of the text
		data['Line'] = data.Line.apply( lambda phrase: self.pretraitement(phrase, nlp, spacy_stopwords) )
		return data

	# Pretreatment of our data (lemme and stopwords)
	def pretraitement(self, phrase, nlp, spacy_stopwords):
		tokens = [ word.lemma_.lower() for word in nlp(phrase) if word.text.lower() not in spacy_stopwords ]
		return ' '.join(tokens)

	# Get our datas
	def getData(self):
		# Searching our .csv file
		df1 = pd.read_csv('api/data/south-park/south-park-dialogues.csv')
		# Retrieve all of our files into a variable
		data = pd.concat( [df1[0:2000]] ) # We take only the 2 000 first lines, else it's too long to treat
		data.sample(1)
		# Getting only characters and lines
		data = data[['Character','Line']].copy()
		# Return our data
		return data

	def getMostCommonData(self, number):
		# Getting the words of all of our data
		words = []
		data = self.get()
		for x in data.itertuples() :
				# Word by word
				sentence = x.Line.split(" ")
				for word in sentence :
					# Without punctuation and spaces
					if word not in '!,...?":;0123456789\\\n':
						words.append(word)

		# Getting the most common words of our data
		freq = nltk.FreqDist(words)
		return freq.most_common(number)

	# Get the data of a specific character
	def getDataCharacter(self, c):
		data = self.get() # Get all the data
		characterData = [] # Prepare his words
		for x in data.itertuples() : # Browse all the data
			if x.Character == c : # If the data is the character one
				# Word by word
				sentence = x.Line.split(" ") # split the words
				for word in sentence :
					# Without punctuation and spaces
					if word not in '!,...?":;0123456789\\\n': # if it's not a punctuation
						characterData.append(word) # we take it
		return characterData

# Return the vocabulary of a character
@api.route('/vocabulary/<c>')
@api.doc(params={'c': 'A Character'})
class characterVocabulary(Resource):
	def get(self, c):
		# Loading our datas
		dataObject = getDatas() # Our object
		freqTotal = dataObject.getMostCommonData(30) # The 30 most common words of our data
		characterData = dataObject.getDataCharacter(c) # The data of a character

		# Getting the FreqDist of this character
		freqCharacter = nltk.FreqDist(characterData)	

		# Browse our most common character words
		# Delete it if it's too common
		i = 0
		toDelete = []
		for word in freqCharacter :
			for word2, freq2 in freqTotal :
				# If the most common words of a character is in the most common words
				# of the serie, we remove it
				if word == word2 : 
					toDelete.append(word) # First we add it to a list during the iteration
			i += 1

		# Then we delete it
		for element in toDelete:
			freqCharacter.pop(element)
		# Getting the 10 most common words of this character
		vocabulary = freqCharacter.most_common(10)
		# Return the vocabulary of the character
		return vocabulary

# Après on cherchera à calculer l'importance d'un personnage dans la série


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int("5000"), debug=True)

