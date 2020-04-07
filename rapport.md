# **Rapport ECIB1 Samuel Platon - DEVOPS4 API**
 





## **Faire fonctionner le projet :**

Pour faire fonctionner le projet, il est nécessaire de lancer les requirements afin d'installer ces paquets supplémentaires :
pandas, spacy, nltk, gensim
Il est aussi nécéssaire de faire 'python3 -m spacy download en_core_web_md' afin de télécharger les stopwords

**/!\ Mon API ne travaille que sur les données de South Park**   

**/!\ Pour que ce projet fonctionne, voici comment doivent être placées ces données : 'api/data/south-park/south-park-dialogues.csv'**   

**/!\ Il est possible que certaines fonctionnalités aient un temps de traitement relativement long (~1 minute)**   


## **Fonctionnalités :** 

En paramètres, <c> représente un personnage, <s> un numéro de saison et <e> un numéro d'épisode.

### Vocabulaire d'un personnage :speech_balloon: :

	**Route :** 0.0.0.0:5000/vocabulary/<c>/<s>/<e> *(exemple : 0.0.0.0:5000/vocabulary/Cartman/10/1)*
	Nb : Pour cette fonctionnalités les mots traités sont lemmatisés et les stopwords retirés.
	Par rapport à un épisode, cette fonctionnalité prend les 10 mots les plus prononcés et les enlève des mots les plus prononcés de notre personnage <c> dans l'épisode. Puis nous retournons les 10 mots les plus prononcés restants de notre personnage <c> de cet épisode, ce qui permet d'obtenir un vocabulaire non pas général mais réellement représentatif d'un personnage pour un épisode.

### Retrouver le personnage :eyes: : 
	**Route :** 0.0.0.0:5000/findCharacter
	Nb : Pour cette fonctionnalités, les mots traités sont lemmatisés et les stopwords retirés.
	Une fois entré dans cette route, notre terminal va nous demander d'entrer une chaîne de caractère, une fois ceci fait, il retournera toutes les lignes de dialogue comprenant cette chaîne sous la forme 'Saison x Episode x | Personnage : Ligne de dialogue'
	Cette fonctionnalité peut être utile pour trouver une expression ou des caractères spécifiques d'un personnage (ex : mom pour cartman) ou d'un episode (ex : hybrid pour l'épisode 2 de la saison 10). 

### Trouver le sujet :book: :
	**Route :** 0.0.0.0:5000/topic/<s>/<e> *(exemple : 0.0.0.0:5000/topic/10/1)*
	Nb : Pour cette fonctionnalités, les dialogues ne sont pas traités et sont rendus tel quel
	Cette route permet, pour un épisode donné, de retourner les trois 'groupe de sujets' les plus probables pour l'épisode et de présenter les 10 mots de chacun de ces 'groupe de sujets', ainsi pour l'épisode 10 de la saison 2 où la famille de Kyle déménage à san francisco après avoir acheté une voiture hybride, tout cela à cause d'un soucis de pollution, on retrouve bien les mots clés 'san francisco', 'kyle', 'smug', 'hybrid', 'car'.

### Bonus : Temps de parole :clock130: :  
	**Route :** 0.0.0.0:5000/timeSpeech
	Nb : Pour cette fonctionnalités, les dialogues ne sont pas traités et sont rendus tel quel
	Cette route permet de retourner en % le temps de parole des 10 personnages parlant le plus dans l'intégralité de la série.
	Cela permet de se rendre compte réellement de l'importance des personnages dans une série, ainsi on peut voir que Cartman a un temps de parole de 16% alors qu'en deuxième place, Stan parle deux fois moins avec un temps de parole de 8%. Si on compare les résultats de toute la série avec un épisode en particulier, on pourrait réussir à trouver les épisodes caractéristiques de personnages (ex : S10E01 pour Chef, S10E02 pour Kyle) etc...

## **Démarche de travail :**

Ma démarche de travail pour mon API a été de développer une classe par fonctionnalité, contenant chacunes une ou plusieurs méthodes selon le besoin au niveau de la propreté du code et toutes rigoureusement commentées en anglais. Une classe getData ne contenant pas de route est aussi créée étant la base de mon API, elle permet de récupérer tous les dialogues, les prétraiter, ou encore de récupérer les dialogues spécifiques à un épisode, ou à un couple épisode / personnage etc...

## **Organisation du développement :**

En terme d'organisation de développement, j'ai travaillé sur les fonctionnalités une à une, en implémentant leur documentation swagger petit à petit et en faisant des tests seulement manuel, les classes de test étant arrivées après. Chacunes des fonctionnalités possède sa branche, de même pour d'autres options (documentation, swagger, récupération de données...).

## **Priorités :** 
Ma priorité dans ce projet d'API a été de développer les fonctionnalités et de les faire marcher, pour cela je suis resté sur le jeu 'South Park' uniquement. Etant moins à l'aise sur le fonctionnement des tests ou de la configuration de l'API, j'y ai alors passé moins de temps.

##**Difficultées rencontrées :**
Ma principale difficulté rencontrée a été la prise en main de l'API afin de comprendre son fonctionnement.