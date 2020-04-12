FROM python:3.6.9

WORKDIR /app

ADD . /app

RUN apk add --no-cache --virtual .build-deps gcc musl-dev
RUN python3 -m pip install cython

RUN pip install -r requirements.txt

RUN python3 -m spacy download en_core_web_md

CMD ["python","api/app.py"]
