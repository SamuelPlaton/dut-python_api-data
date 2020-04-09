from urllib.parse import urlencode
import json
import pytest

def call(client, path, params):
  url = path + '?' + urlencode(params)
  response = client.get(url)
  return json.loads(response.data.decode('utf-8'))

def test_timeSpeech(client):
	result = call(client, '/timeSpeech', {})
	assert result == {
    "Cartman": "20.19%",
    "Kyle": "7.3%",
    "Stan": "5.99%",
    "Randy": "4.01%",
    "Mrs. Garrison": "2.55%",
    "Butters": "2.28%",
    "Mr. Mackey": "2.14%",
    "Al Gore": "1.77%",
    "Liane": "1.73%",
    "Mr. Connolly": "1.64%"
}

def test_vocabulary(client):
	result = call(client, '/vocabulary/Stan/10/1', {})
	assert result == [
    [
        "come",
        4
    ],
    [
        "guy",
        3
    ],
    [
        "say",
        3
    ],
    [
        "good",
        3
    ],
    [
        "sex",
        3
    ],
    [
        "join",
        2
    ],
    [
        "dude",
        2
    ],
    [
        "look",
        2
    ],
    [
        "maybe",
        2
    ],
    [
        "need",
        2
    ]
]