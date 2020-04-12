FROM python:3.6.9

WORKDIR /app

ADD . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN python3 -m spacy download en_core_web_md

CMD ["python","api/app.py"]
