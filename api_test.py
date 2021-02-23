import requests
import json

data = {
    "userId": 1,
    "id": 100,
    "title": "Kavichki",
    "body": "Test assignment for Kavichki"
}

def test_get_request():
    r = requests.get('http://jsonplaceholder.typicode.com/posts/1')
    assert r.status_code == 200
    assert r.text == open('./json_get_example.json', 'rt', encoding='UTF-8').read()

def test_post_request():
    r = requests.post('http://jsonplaceholder.typicode.com/posts', data=data)
    dict = json.loads(r.text)
    assert dict['userId'] == '1'
    assert dict['id'] == 101
    assert dict['title'] == 'Kavichki'
    assert dict['body'] == 'Test assignment for Kavichki'
