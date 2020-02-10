from urllib.parse import urlencode
import json
import pytest

def call(client, path, params):
  url = path + '?' + urlencode(params)
  response = client.get(url)
  return json.loads(response.data.decode('utf-8'))

# Test fonction plus_one
def test_plus_one(client):
    """Start with a blank database."""
    result = call(client, '/plus_one/5', {})
    assert result == 6

# Test fonction square
def test_square(client):
    """Start with a blank database."""
    result = call(client, '/square/5', {})
    assert result == 25