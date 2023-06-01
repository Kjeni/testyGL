import pytest
import requests
import pytest_check as check
import logging
from typing import Optional
import json
from utils import BASE_URL, GOREST_HEADERS, ANONYMOUS_HEADERS, get_random_existing_id, \
    generate_random_string, generate_random_email, create_random_resource, \
    find_element_in_json, Comment


LOGGER = logging.getLogger(__name__)
URL = BASE_URL + "comments"

@pytest.fixture()
def create_comment():
    post_info = create_random_resource("comment")
    comment_id = str(find_element_in_json("id", post_info.text))  
    yield comment_id


@pytest.fixture()
def create_delete_after_post():
    post_info = create_random_resource("comment")
    comment_id = str(find_element_in_json("id", post_info.text))
    yield comment_id
    delete_url = URL + "/" + comment_id
    requests.delete(delete_url, headers=GOREST_HEADERS)


random_id = get_random_existing_id("post")
parameters_lists = [(random_id, "Name Surname", "hello@hello.pl", "We won"),
                    (random_id, "OnlyName", "hello@hello.pl", "Is it fair?"),
                    (random_id, "Oh", generate_random_email(),  generate_random_string(10))
                    ]


@pytest.mark.tc30
@pytest.mark.parametrize("expected_id, expected_name, expected_email, expected_body", parameters_lists)
def test_add_new_comment(expected_id, expected_name, expected_email, expected_body):
    COMMENT_DICT = dict(Comment(post_id=expected_id, name=expected_name, email=expected_email, body=expected_body))

    payload = json.dumps(COMMENT_DICT)
    response = requests.post(URL, headers=GOREST_HEADERS, data=payload)

    assert response.status_code == 201  # created
    assert expected_id, expected_name in response.text
    assert expected_email, expected_body in response.text
    comment_id = str(find_element_in_json("id", response.text))
    delete_url = URL + "/" + comment_id
    requests.delete(delete_url, headers=GOREST_HEADERS)


@pytest.mark.tc30
def test_add_new_comment_id_based(post_id: Optional[str] = None):
    if not post_id:
        response = create_random_resource("comment")
    else:
        response = create_random_resource("comment", post_id)
        logging.info(response.text)

    assert response.status_code == 201  # created assert page_response.status_code == 200 or check.equal(response.status_code, 201)
    comment_id = str(find_element_in_json("id", response.text))
    delete_url = URL + "/" + comment_id
    response = requests.get(delete_url, headers=GOREST_HEADERS)
    assert response.status_code == 200 #assert page_response.status_code == 200 or check.equal(response.status_code, 200)
    return comment_id


def test_add_new_user_id_based():
    response = create_random_resource("user")
    logging.info(response.text)

    check.equal(response.status_code, 201)  # created
    user_id = str(find_element_in_json("id", response.text))
    delete_url = BASE_URL + 'users' + "/" + user_id
    response = requests.get(delete_url, headers=GOREST_HEADERS)
    check.equal(response.status_code, 200)
    return user_id


def test_add_new_post_id_based(user_id: Optional[str] = None):
    if not user_id:
        response = create_random_resource("post")
    else:
        response = create_random_resource("post", user_id)
        logging.info(response.text)

    check.equal(response.status_code, 201)  # created
    comment_id = str(find_element_in_json("id", response.text))
    delete_url = BASE_URL + 'posts' + "/" + comment_id
    response = requests.get(delete_url, headers=GOREST_HEADERS)
    check.equal(response.status_code, 200)
    return comment_id


@pytest.mark.tc49
def test_update_existing_user(user_id: Optional[str] = None):
    test_body = "Should pass."
    test_email = generate_random_email()
    if not user_id:
        resource_response = create_random_resource('user')
        resource_id = str(find_element_in_json("id", resource_response.text))
    else:
        resource_id = user_id

    keys = ["id", "name", "email"]
    values = [resource_id, test_body, test_email]
    data_dict = dict(zip(keys, values))

    url = BASE_URL + 'users' + "/" + resource_id
    payload = json.dumps(data_dict)
    response = requests.patch(url, headers=GOREST_HEADERS, data=payload)
    logging.info(f'Updating user(PATCH) for testing. Status code is{response.status_code}')
    check.equal(response.status_code, 200)  # created
    check.is_in(test_body, response.text)
    response = requests.get(url, headers=GOREST_HEADERS)
    check.is_in(test_body, response.text)


def test_update_existing_post(post_id: Optional[str] = None):
    test_body = "Should pass."
    if not post_id:
        resource_response = create_random_resource('post')
        resource_id = str(find_element_in_json("id", resource_response.text))
        logging.info(resource_id)
    else:
        resource_id = post_id

    keys = ["id", "body"]
    values = [resource_id, test_body]
    data_dict = dict(zip(keys, values))

    url = BASE_URL + 'posts' + "/" + resource_id
    payload = json.dumps(data_dict)
    response = requests.patch(url, headers=GOREST_HEADERS, data=payload)
    logging.info(f'Updating post(PATCH) for testing. Status code is{response.status_code}')
    check.equal(response.status_code, 200)  # created
    check.is_in(test_body, response.text)
    response = requests.get(url, headers=GOREST_HEADERS)
    check.is_in(test_body, response.text)


@pytest.mark.tc31
def test_update_existing_comment(comment_id: Optional[str] = None):
    test_body = "Should pass."
    if not comment_id:
        resource_response = create_random_resource('comment')
        resource_id = str(find_element_in_json("id", resource_response.text))
    else:
        resource_id = comment_id

    keys = ["id", "body"]
    values = [resource_id, test_body]
    data_dict = dict(zip(keys, values))

    url = URL + "/" + resource_id
    payload = json.dumps(data_dict)
    response = requests.patch(url, headers=GOREST_HEADERS, data=payload)
    logging.info(f'Updating comment(PATCH) for testing. Status code is{response.status_code}')
    check.equal(response.status_code, 200)  # created
    check.is_in(test_body, response.text)
    response = requests.get(url, headers=GOREST_HEADERS)
    check.is_in(test_body, response.text)


@pytest.mark.tc34
def test_get_first_page_comments_without_authentication():
    page_url = URL + "?page=1"
    page_response = requests.get(page_url, headers=ANONYMOUS_HEADERS)
    assert page_response.status_code == 200  # everything as expected

@pytest.mark.parametrize("expected_headers, expected_code",
                         [(GOREST_HEADERS, 204),
                          (ANONYMOUS_HEADERS, 404)])
@pytest.mark.tc35
def test_delete_user_comment(create_comment, expected_headers, expected_code):
    comment_id = create_comment
    delete_url = URL + "/" + comment_id
    response = requests.delete(delete_url, headers=expected_headers)
    assert response.status_code == expected_code  # no content or couldn't delete depending on authentication