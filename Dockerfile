FROM python:3.6.9-alpine

WORKDIR /app

ADD . /app

RUN apk add --no-cache --virtual .build-deps gcc musl-dev
RUN python3 -m pip install cython

RUN pip install -r requirements.txt

RUN pip3 install pandas
RUN pip3 install spacy
RUN pip3 install nltk
RUN pip3 install gensim
RUN python3 -m spacy download en_core_web_md
CMD ["python","api/app.py"]
