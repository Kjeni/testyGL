import re
import json
import requests
import random
import string
from typing import Union
from concurrent.futures import ThreadPoolExecutor
import logging

LOGGER = logging.getLogger(__name__)

BASE_URL = "https://gorest.co.in/public/v1/"
GOREST_TOKEN = 'da8e2ff091bf79d8d75b9dfbee574fcb44e203053778f0af358cbc0da5a7f0e7'

GOREST_HEADERS = {
    'Authorization': f'Bearer {GOREST_TOKEN}',
    'Content-Type': 'application/json'
}

ANONYMOUS_HEADERS = {
    'Content-Type': 'application/json'
}


class User():

    def __init__(self, email=None, name=None, gender=None, status=None):
        self.name = name if name is not None else generate_random_string(12)
        self.email = email if email is not None else generate_random_email()
        self.gender = gender if gender is not None else random.choice(('male', 'female'))
        self.status = status if status is not None else random.choice(('active', 'inactive'))

    def __iter__(self):
        yield 'email', self.email
        yield 'name', self.name
        yield 'gender', self.gender
        yield 'status', self.status

    def __str__(self):
        return f'Myclass User, email: {self.email}, name: {self.name}, gender: {self.gender}, status: {self.status}'


class Todo():

    def __init__(self, user_id=None, title=None, email=None, due_on=None, status=None):
        self.user_id = user_id if user_id is not None else get_random_existing_id('user')
        self.title = title if title is not None else generate_random_string(12)
        self.email = email if email is not None else generate_random_email()
        self.due_on = due_on if due_on is not None else random.choice \
            (('2022-02-18T00:00:00.000+05:30', '2022-02-14T00:00:00.000+05:30'))
        self.status = status if status is not None else random.choice(('completed', 'pending'))

    def __iter__(self):
        yield 'user_id', self.user_id
        yield 'title', self.title
        yield 'email', self.email
        yield 'due_on', self.due_on
        yield 'status', self.status


    def __str__(self):
        return f'Myclass Todo, user_id: {self.user_id}, title: {self.title}, email: {self.email}, due_on: {self.due_on}, status: {self.status}'


class Post():

    def __init__(self, user_id=None, title=None, body=None):
        self.user_id = user_id if user_id is not None else get_random_existing_id('user')
        self.title = title if title is not None else generate_random_string(12)
        self.body = body if body is not None else generate_random_string(40)

    def __iter__(self):
        yield 'user_id', self.user_id
        yield 'title', self.title
        yield 'body', self.body

    def __str__(self):
        return f'Myclass Post, user_id: {self.user_id}, title: {self.title}, body: {self.body}'


class Comment():

    def __init__(self, post_id=None, name=None, email=None, body=None):
        self.post_id = post_id if post_id is not None else get_random_existing_id('post')
        self.name = name if name is not None else generate_random_string(12)
        self.email = email if email is not None else generate_random_email()
        self.body = body if body is not None else generate_random_string(12)

    def __iter__(self):
        yield 'post_id', self.post_id
        yield 'name', self.name
        yield 'email', self.email
        yield 'body', self.body

    def __str__(self):
        return f'Myclass Comment, post_id: {self.post_id}, name: {self.name}, email: {self.email}, body: {self.body}'


def find_element_in_text(element: str, response_data: str) -> Union[list, Exception]:
    """
    find element in text using a regex. To be used with not deeply nested API.
    Element is searched by regex (?<=\"{element}":).*?(?=,)
    :param element:
    :param response_data:
    :return: list or an error

    example:
        list_of_ids = find_element_in_text("id", response.text)
        random_id_1, *_ = find_element_in_text("id", response.text)
    """
    regex_element = f"""(?<=\"{element}":).*?(?=,)"""
    matches = re.findall(regex_element, response_data)
    return matches


def find_element_in_json(element: str, response_data:str)-> Union[int, Exception]:
    """
    find element in response text, if it is nested under ['data'].
    :param element: what we want to find
    :param response_data: response text
    example:
        random_id_1= find_element_in_text("id", response.text)
    """
    responseJson = json.loads(response_data)
    logging.info(response_data)
    resource_id = responseJson["data"][element]
    return resource_id


def generate_random_string(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))  # based on Aleksandra & Paweł


def generate_random_email():
    return generate_random_string(12).lower() + '@' + "gmail.com"  # based on Paweł


def get_random_existing_id(resource_type: str):
    """
    return a first existing id from a first page or results returned by API
    :param resource_type - user, post, todo or comment
    example:
        post_id = get_random_existing_id("post")
    """
    url = BASE_URL + resource_type + 's' + "?page=1"
    response = requests.get(url, headers=GOREST_HEADERS)
    responseJson = json.loads(response.text)
    resource_id = responseJson["data"][0]['id']
    return resource_id


def generate_resource_data(resource, resource_id):
    data_list = [resource, resource_id]
    try:
        match resource:
            case "user":
                new_user = User()
                data_dict = dict(new_user)
            case "todo":
                requirement = 'user'
                new_todo = Todo(user_id=resource_id) if resource_id is not None else Todo()
                data_dict = dict(new_todo)
            case "post":
                requirement = 'user'
                new_post = Post(user_id=resource_id) if resource_id is not None else Post()
                data_dict = dict(new_post)
            case "comment":
                requirement = 'post'
                new_comment = Comment(post_id=resource_id) if resource_id is not None else Comment()
                data_dict = dict(new_comment)
    except TypeError:
        logging.info(f'There might be no {requirement} right now. To create a {resource}, create {requirement} first')
    return data_dict


def create_random_resource(resource: str, resource_id=None):
    data_dict = generate_resource_data(resource, resource_id)
    endpoint = resource + 's'
    payload = json.dumps(data_dict)
    url = BASE_URL + endpoint
    response = requests.post(url, headers=GOREST_HEADERS, data=payload)
    logging.info(f'Generating random {resource} for testing. Status code is: {response.status_code}')
    print(f'Generating random {resource} for testing. Status code is: {response.status_code}')
    return response


def get_url(_url):
    return requests.get(_url)

