import pytest

@pytest.fixture
def client():
  from api import app
  app.app.config['TESTING'] = True
  return app.app.test_client()