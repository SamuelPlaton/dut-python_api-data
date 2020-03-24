# Voicii un exemple comptet, mais simple, d'une API permettant de gérer une liste de TODO. 
# Dans cet exemple, vous avez ce qu'il vous faut pour construire l'API de votre projet et la documenter correctement. 
# J'ai commenté pour vous certaines sections du code pour que vous puissiez le comprendre. N'hésitez pas à poser des questions. 

# Pour rappel la documentation de Flask-restplus est ici : https://flask-restplus.readthedocs.io/en/stable/index.html
# Cette exemple est tirée de cette documentation, vous trouvez des précisions supplémentaires sur toutes les fonctions dans la doc. 

# Dans un premier temps, copiez ce code dans un nouveau fichier de votre dossier api. 
# Lancez le serveur Flask (python api/todo.py) et regardez la documentation générée (http://localhost:5000)
# Notez que la documentation swagger est en deux parties : opérations et models 
# Testez chaque fonctionnalité, observez chaque requête et étudiez le code pour comprendre son fonctionnement. 

# L'exemple vous donne le code de plusieurs verbes HTTP correspondants à diverses actions : 
# GET (lecture)
# POST(écriture, envoie d'information)
# PUT(mise à jour)
# DELETE(suppression)

# Certaines ne seront pas utiles à vos projets. Etudiez surtout la manière dont fonctionnent les verbes GET naturellement et 
# POST (comment sont envoyés les paramètres à l'API lors de la requête ?)


from flask import Flask
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix

# Création de l'API, documentation minimale utile à Swagger. 
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API',
)

# Création d'un namespace, deux utilités : 
# - création d'un namespace de routes /todos (localhost:5000/todos) qui sera ensuite utilisé ensuite avec @ns.route
# - création d'un namespace dans la documenation swagger (TODO operations)
ns = api.namespace('todos', description='TODO operations')


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
# Il serait possible (voire intéressant...) de décrire cette classe dans un

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

# Initialisation de la classe, création de TODO par défaut.
DAO = TodoDAO()
DAO.create({'task': 'Build an API'})
DAO.create({'task': '?????'})
DAO.create({'task': 'profit!'})

# Dans le namespace @ns (/todos donc) déclaration de la route / avec deux verbes HTTP, un Get, un POST
@ns.route('/')
class TodoList(Resource):
    # Notez cette docstring qui sert directement à la documentation swagger.
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    # Fonction marshall_with (https://flask-restplus.readthedocs.io/en/stable/marshalling.html) 
    # qui à l'aide du modèle (ici todo) déclaré plus haut, se charge de : 
    # - sérialiser la réponse (renvoyer la liste en JSON)
    # - Documenter la fonction en Swagger
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        return DAO.todos
    # Route de création d'un TODO (en POST donc)
    @ns.doc('create_todo')
    # l'API attend un objet de type TODO en paramètre
    @ns.expect(todo) 
    # Cette fonction décode l'objet reçu automatiquement en fonction du modèle
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        # On envoie les paramètres décodés (ici contenu dans le body de la requête POST, vous pouvez tester dans l'interface Swagger)
        # A la fonction de création dans la classe DAO
        return DAO.create(api.payload), 201


# Seconde série de routes, qui cette fois attendent toute un paramètre id (entier) donc :
# http://localhost:5000/todos/<int>
@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    # Récupération d'un TODO, notez le paramètre ID, insérez automatiquement depuis la route. 
    # Notez également l'usage de la fonction mashal_with, qui la encore fait la sérialisation.
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    # Suppression d'un TODO
    # Ici l'API retourne '' et un statut 204 en cas de soucis. 
    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    # Mise à jour d'un TODO (fonctionnement très similaire à la création, avec un paramètre ID supplémentaire)
    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)


if __name__ == '__main__':
    app.run(debug=True)