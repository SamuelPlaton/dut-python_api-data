FROM python:3.6.9-alpine

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

CMD ["python","api/app.py"]
