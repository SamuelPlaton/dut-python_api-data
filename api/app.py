from flask import request, Flask, jsonify
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
import requests

import json
import string
import csv 
import pandas as pd # pip3 install pandas
import spacy #pip3 install spacy ET python3 -m spacy download en_core_web_md
import nltk #pip3 install nltk
from flask_swagger import swagger
from gensim.corpora import Dictionary #pip3 install gensim
from gensim.utils import simple_preprocess
from gensim.models import LdaModel

# Création de l'API, documentation minimale utile à Swagger.
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='ECI API',
  description='API de projet DEVOPS4 - ECI B1 Samuel Platon',
)


# Retrieve and pretreat data
@api.doc(doc={"Class used to retrieve and pretreat datas"})
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
		data = pd.concat( [df1[0:4000]] ) # We take only the 4 000 first lines, else it's too long to treat
		data.sample(1)
		# Getting the desired data
		data = data[['Season', 'Episode', 'Character','Line']].copy()
		# Return our data
		return data

	@api.doc(params={'number': 'The number of common words', 's' : 'number of the season', 'e': 'number of the episode'})
	def getMostCommonData(self, number, s, e):
		# Getting the words of an episode
		words = []
		data = self.get()
		for x in data.itertuples() :
				# Word by word
				sentence = x.Line.split(" ")
				for word in sentence :
					if x.Season == s and x.Episode == e:
						# Without punctuation and spaces
						if word not in '!,...?":;0123456789\\\n':
							words.append(word)

		# Getting the most common words of our data
		freq = nltk.FreqDist(words)
		return freq.most_common(number)

	# Get the data of a specific character in a specific episode
	@api.doc(params={'c': 'A Character', 's' : 'number of the season', 'e': 'number of the episode'})
	def getDataCharacter(self, c, s, e):
		data = self.get() # Get all the data
		characterData = [] # Prepare his words
		for x in data.itertuples() : # Browse all the data
			if x.Character == c and x.Season == s and x.Episode == e: # If the data is the character one
				# Word by word
				sentence = x.Line.split(" ") # split the words
				for word in sentence :
					# Without punctuation and spaces
					if word not in '!,...?":;0123456789\\\n': # if it's not a punctuation
						characterData.append(word) # we take it
		return characterData

	# Get the data of a specific episode
	@api.doc(params={'data' : 'the data of the serie', 's' : 'number of the season', 'e': 'number of the episode'})
	def getDataEpisode(self, data, s, e):
		data = self.get() # Get all the data
		episodeData = [] # Prepare his words
		for x in data.itertuples() : # Browse all the data
			if x.Season == s and x.Episode == e: # If the data is the character one
				# Word by word
				sentence = x.Line.split(" ") # split the words
				for word in sentence :
					# Without punctuation and spaces
					if word not in '!,...?":;0123456789\\\n': # if it's not a punctuation
						episodeData.append(word) # we take it
		return episodeData

	# Return the number of total words in the data
	@api.doc(params={'data': 'The data of the whole serie'})
	def totalWords(self, data):
		totalWords = 0
		for x in data.itertuples():
			words = x.Line.split(" ")
			totalWords += len(words)
		return totalWords

# Return the vocabulary of a character in a episode of a season
@api.route('/vocabulary/<c>/<s>/<e>', doc={"description": "Return the vocabulary of a character in a episode of a season"})
@api.doc(params={'c': 'A Character', 's' : 'number of the season', 'e': 'number of the episode'})
class characterVocabulary(Resource):
	def get(self, c, s, e):
		# Loading our datas
		dataObject = getDatas() # Our object
		freqTotal = dataObject.getMostCommonData(10, s, e) # The 10 most common words of our episode
		characterData = dataObject.getDataCharacter(c, s, e) # The data of a character in a episode

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

# We are trying to find which character say the sentence in input
@api.route('/findCharacter', doc={"description": "find which caracters say the sentencu in input (terminal) in which seasons/episodes"})
class characterRecognition(Resource):
	def get(self):
		# Loading our datas without treatment
		dataObject = getDatas()
		data = dataObject.getData()

		# We are setting our list of characters
		characters = []

		# We ask the user to put a sentence in the terminal
		sentence = input()
		# We browse our data
		for x in data.itertuples() :
			# If we find which character said the sentence
			if sentence.lower() in x.Line.lower():
				# We add him and the sentence to the list
				characters.append("Season "+x.Season+" Episode "+x.Episode+" | "+x.Character+" : "+x.Line)
		# Then we return the list
		return characters

# We try to calculate the % on speech of the 10 most importants characters
# It's the 4th "free" function, it's useful to see really which characters are in the middle
# of theses series and by how much, we try to quantify the importance of a character here
# This data can be useful in the future if we want to see if a character has a specific episode about him
@api.route('/timeSpeech', doc={"description": "find the % time of speech of the 10 most important characters"})
class timeSpeech(Resource):
	def get(self):
		# Loading our datas without treatment
		dataObject = getDatas()
		data = dataObject.getData()
		totalWords = dataObject.totalWords(data)

		# Getting a dict() of all characters and number of Words
		charactersLines = self.separateCharacters(data)
		df = pd.DataFrame.from_dict(charactersLines, orient='index')
		df = df.sort_values(by=["Total"], ascending=False)
		# Picking only the 10 who speak the most
		df = df[0:10]
		# Getting now the frequency with totalWords
		freq = dict()
		for character, value in df.itertuples():
			freq[character] = str(round((value/totalWords)*100, 2))+"%"
		# Returning our frequency
		return freq

	@api.doc(params={'data': 'The data of our serie'})
	def separateCharacters(self, data):
		charactersLines = dict()

		for x in data.itertuples():
			charactersLines[x.Character] = {"Total" : 0}

		for x in data.itertuples():
			words = x.Line.split(" ")
			charactersLines[x.Character] = {"Total" : charactersLines[x.Character]["Total"]+len(words)}
		return charactersLines

# Topic Model of an episode of a season
@api.route('/topic/<s>/<e>', doc={"description": "find the topic of an episode"})
@api.doc(params={'s' : 'number of the season', 'e': 'number of the episode'})
class topicModel(Resource):
	def get(self, s, e):
		# Loading our datas without treatment
		dataObject = getDatas()
		data = dataObject.get()
		dataEpisode = dataObject.getDataEpisode(data, s, e)
		
		# preprocess of the words of the episode
		tokenEpisode= []		
		tokenEpisode.append([token for token in self.preprocessEpisode(dataEpisode)])
		dictionnaryEpisode = Dictionary(tokenEpisode)

		# creating our model corpus
		model_corpus = []
		for episode in tokenEpisode:
			model_corpus.append(dictionnaryEpisode.doc2bow(episode))

		# Creating our list of topics with the LDA models
		topicsList = []
		string = "Voici les sujets recurrents pour l'episode "+e+" de la saison "+s
		topicsList.append(string)
		lda_model = LdaModel(corpus=model_corpus, id2word=dictionnaryEpisode, num_topics=3) # We choose to get only the 3 most significant topics
		for topic_id, topic_keywords in lda_model.show_topics(formatted=False):
			string = "=== Pour le sujet au mot clé principal '"+str(lda_model.show_topic(topic_id, topn=1)[0][0])+"', les mots clefs representatifs sont ==="
			topicsList.append(string)
			# Broswe the keywords of each topic
			for keyword in topic_keywords:
				string = "-> "+str(keyword[0])+" ("+str(keyword[1])+")"
				topicsList.append(string)
		# Return our list of topics
		return topicsList

	@api.doc(params={'data': 'The data of an episode'})
	def preprocessEpisode(self, data):
		# Join our tokens in a single string in order to do a simple preprocess
		data = " ".join(data)
		data = simple_preprocess(data)
		# Loading our stopwords
		nlp = spacy.load("en_core_web_md") # loading the english model
		spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
		# Returning our tokens without the spacy stopwords
		return [token for token in data if token not in spacy_stopwords]







if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int("5000"), debug=True)

