from urllib.parse import urlencode
import json
import pytest

def call(client, path, params):
  url = path + '?' + urlencode(params)
  response = client.get(url)
  return json.loads(response.data.decode('utf-8'))

def test_timeSpeech(client):
	result = call(client, '/timeSpeech', {})
	print(result)
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