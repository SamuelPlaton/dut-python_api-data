# TP2 Continuous build
# TP2 (S6) - Integration continue

Durant ce TP, nous allons mettre en place une application (API) très simple, qui sera intégrée en continue à l'aide de Gitlab CI. 

## Mise en place de votre API

Afin de vous familiariser avec cette technologie qui sera requise pour les projets (partie ADM), nous utiliserons le micro framework [Flask](https://flask.palletsprojects.com/en/1.1.x/)

- Sur la base du code présent dans le dossier TP2_base et de la documentation de Flask, mettez en place une API dotée des fonctions suivantes : 
	- plus_one ('/plus_one') qui ajoute un à un entier x passé en paramètre
	- square ('/square') qui renvoie le carré d'un entier x passé en paramètre. 
- Ecrivez les tests (dans le fichier `test/test_api.py`) de ces deux fonctions à l'aide de la documentation de Flask, la fonction `client()` est déjà écrite (voir fichier `test/conftest.py`. 
- Vérifiez le bon fonctionnement de l'API en lançant le serveur de développement de Flask (`python api/app.py`)
- L'installation de Flask et pytest peut se faire par les requirements (pip install -r requirements.txt), ajoutez l'option --user sur les machines de l'IUT. Pytest se lance par la commande `pytest` (ou `python -m pytest` sur les machines de l'IUT).




## Intégration continue 

Afin de mettre en place l'intégration continue, nous utiliserons Gitlab CI. Gitlab CI requiert l'installation sur une machine (autre que la machine qui héberge Gitlab) d'un Gitlab Runner. Ce runner va se charger de toutes les opérations d'intégration pour builder et déployer votre application. Le runner vérifie lui même à interval régulier si des jobs sont en attente sur la plateforme Gitlab. 

### Installation du runner

Le runner peut être installé de différentes manières, via un paquet de l'OS ou via un container Docker. Pour des raisons de droits d'accès en root, nous utiliserons la procédure via le container docker. 

```bash
docker run -d --name gitlab-runner --restart always \
  -v /srv/gitlab-runner/config:/etc/gitlab-runner \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gitlab/gitlab-runner:latest
```

- Détaillez le fonctionnement de cette commande, à quoi servent les différentes options ?

### Registering du runner 

Une fois ce runner installé et exécuté (docker ps pour le vérifier). Il faut l'inscrire (register) pour que Gitlab en est connaissance. Créez sur la forge de l'IUT un dépot pour votre API Flask. Dans Settings -> CI/CD Gitlab vous donne deux informations importantes, l'URL et un ID qui vont vous permettre d'inscrire votre dépot à l'aide de la commande suivante (ici dans sa version docker), pensez à remplacer le TOKEN. la configuration est écrite dans le dossier /srv de la machine, vous pouvez la déplacer dans un répertoire non soumis à des droits si nécessaire. Une fois le container correctement inscrit, vous devez le voir disponible dans la section CI / CD de votre dépot Gitlab. 



```bash
docker run --rm -v /srv/gitlab-runner/config:/etc/gitlab-runner gitlab/gitlab-runner register \
  --non-interactive \
  --executor "docker" \
  --docker-image docker:stable \
  --url "https://forge.iut-larochelle.fr/" \
  --registration-token "TOKEN" \
  --description "docker-runner" \
  --tag-list "docker" \
  --run-untagged="true" \
  --locked="false" \
  --docker-privileged \
  --docker-volumes "/certs/client" \
  --access-level="not_protected"

```

- Vérifiez dans Gitlab l'existence du runner. 


### Configuration du build 

Ajoutez à votre dépot un fichier .gitlab-ci.yml avec le contenu suivant : 

```yml
image: python:3.6.9-alpine

stages:
  - test

Tests:
  stage: test
  script: 
    - pip install -r requirements.txt
    - pytest
```

Ici nous configurons une étape d'intégration continue, l'exécution des tests. 

- Pushez ces modifications, Gitlab va alors executer via votre runner ce pipeline d'intégration continue. Vérifiez que tout se passe bien depuis l'interface de Gitlab. 


Ajoutez un fichier Dockerfile qui va servir à la construction de l'image (de production) de votre API : 

```bash
FROM python:3.6.9-alpine

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

CMD ["python","api/app.py"]
```

- testez localement le build de l'image en utilisant : `docker build -t devops/api .` et testez l'éxécution du container `docker run --rm -p 5000:5000 --name devops_api devops/api` 

Ajoutez ensuite l'étape de construction de l'image Docker (build) au pipeline et n'oubliez pas d'ajouter la nouvelle étape dans les stages : 

```yml
Build:
  stage: build

  variables: 
    DOCKER_HOST: tcp://docker:2375
    DOCKER_DRIVER: overlay2
    DOCKER_TLS_CERTDIR: ""

  image: docker:stable

  services:
  - docker:dind

  script:
    - docker build -t devops/api .
```

Pushez vos modifications, Gitlab et votre runner exécute cette fois deux stages, les tests et la construction de l'image. 

### Push de l'image sur le docker store

Cette étape, qui vise à pusher l'image de votre API sur le docker hub peut être faite en groupe si vous ne souhaitez pas créer chacun un compte (qui pourrait cela dire vous servir plus tard). 

- Créez donc au moins un compte **par groupe** sur le docker hub. 
- Générez ensuite dans l'espace personnel (une ou plusieurs) clé d'authentification (token) qui remplaceront le mot de passe dans le pipeline. 
- Créez un dépot (public ou privé peu importe) pour votre API.
- Créez dans l'interface de Gitlab les variables REGISTRY_USER et REGISTRY_TOKEN (en mode protégé). 
- Modifiez l'étape de build de votre pipeline pour ajouter le push vers le registry docker, de la manière suivante : 

```bash

  services:
  - docker:dind
  script:
    - docker build -t username/nom_image .
    - echo "$REGISTRY_TOKEN"
    - docker login -u "$REGISTRY_USER" -p "$REGISTRY_TOKEN"
    - docker push username/nom_image
```

- Commitez et pushez vos changements, le pipeline va désormais tester, builder / pusher l'image docker sur le registry docker. Vérifiez la présence de l'image sur le registry en la téléchargeant. 

