import string
import requests
import json
import random

URL = "https://gorest.co.in/public/v1/"
FILE_PATH = f"yourpath/test_large_post.txt"

CREATE_USER_PAYLOAD = {
        "name": "",
        "gender": "",
        "email": "",
        "status": ""
    }
CREATE_USER_POST_PAYLOAD = {
        "user_id": 0,
        "title": "",
        "body": ""
    }
EDIT_POST_PAYLOAD = {
        "id": 0,
        "user_id": 0,
        "title": "",
        "body": ""
}

HEADERS = {
        'Accept': 'application/json',
        'Authorization': 'Bearer 3158f06bdb11ac960e165a306aa8698b94fd7fbfc04eed59aa98b95be56fd72e',
        'Content-Type': 'application/json'
    }


def open_file(filepath):
    with open(filepath, 'r') as file:
        large_post = file.read()
    return large_post


def generate_random_string(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


def generate_random_email():
    return generate_random_string(12).lower() + '@' + "gmail.com"


def generate_body(resource):
    if resource == "user":
        CREATE_USER_PAYLOAD['name'] = generate_random_string(9)
        CREATE_USER_PAYLOAD['gender'] = "male"
        CREATE_USER_PAYLOAD['email'] = generate_random_email()
        CREATE_USER_PAYLOAD['status'] = 'active'
        data = CREATE_USER_PAYLOAD
    elif resource == "invalid_email":
        CREATE_USER_PAYLOAD['name'] = generate_random_string(9)
        CREATE_USER_PAYLOAD['gender'] = "male"
        CREATE_USER_PAYLOAD['email'] = "InvalidEmail.gmail.com"
        CREATE_USER_PAYLOAD['status'] = 'active'
        data = CREATE_USER_PAYLOAD
    elif resource == "taken_email":
        CREATE_USER_PAYLOAD['name'] = generate_random_string(9)
        CREATE_USER_PAYLOAD['gender'] = "male"
        CREATE_USER_PAYLOAD['email'] = use_already_taken_email()
        CREATE_USER_PAYLOAD['status'] = 'active'
        data = CREATE_USER_PAYLOAD
    elif resource == "large_post":
        CREATE_USER_POST_PAYLOAD['user_id'] = use_existing_id("users")
        CREATE_USER_POST_PAYLOAD['title'] = generate_random_string(16)
        CREATE_USER_POST_PAYLOAD['body'] = open_file(FILE_PATH)
        data = CREATE_USER_POST_PAYLOAD
    elif resource == "edit_post_not_by_author":
        EDIT_POST_PAYLOAD['id'] = use_existing_id("posts")
        EDIT_POST_PAYLOAD['user_id'] = use_existing_id("users")
        EDIT_POST_PAYLOAD['title'] = generate_random_string(16)
        EDIT_POST_PAYLOAD['body'] = generate_random_string(200)
        data = EDIT_POST_PAYLOAD
    return data


def use_already_taken_email():
    url = URL+"users"
    response = requests.get(url).json()
    taken_email = response['data'][0]['email']
    return taken_email


def use_existing_id(request_url):
    url = URL + request_url
    response = requests.get(url).json()
    existing_id = response['data'][0]['id']
    return existing_id


def anonymous_get_request(request_url):
    url = URL + request_url
    response = requests.get(url)
    response_json = response.json()
    request_code = response.status_code
    returned_dict = {'code': request_code, 'json': response_json}
    return returned_dict


def create_request(resource, request_url, request_method):
    url = URL + request_url
    data = generate_body(resource)
    payload = json.dumps(data)
    response = requests.request(request_method, url, headers=HEADERS, data=payload)
    response_json = response.json()
    request_code = response.status_code
    returned_dict = {'code': request_code, 'json': response_json}
    return returned_dict
