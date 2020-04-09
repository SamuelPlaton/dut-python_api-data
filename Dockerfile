FROM python:3.6.9-alpine

WORKDIR /app

ADD . /app

RUN pip3 install -r requirements.txt

CMD ["python","api/app.py"]
