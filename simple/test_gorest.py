import pytest
import simple_utils


@pytest.mark.tc01
def test_create_user_already_taken_email():
    response = simple_utils.create_request("taken_email", "users", "POST")
    assert response['code'] == 422
    assert response['json']['data'][0]['message'] == 'has already been taken'


@pytest.mark.tc02
def test_create_user_invalid_email():
    response = simple_utils.create_request("invalid_email", "users", "POST")
    assert response['code'] == 422
    assert response['json']['data'][0]['message'] == 'is invalid'


@pytest.mark.tc03
def test_create_new_user():
    response = simple_utils.create_request("user", "users", "POST")
    assert response['code'] == 201


@pytest.mark.tc20
def test_anonymous_get_request():
    response = simple_utils.anonymous_get_request("todos")
    print(response['json'])
    assert response['code'] == 200


@pytest.mark.tc24
def test_create_large_post():
    response = simple_utils.create_request("large_post", "posts", "POST")
    assert response['code'] == 422
    print(response['json']['data'][0]['message'])
    assert response['json']['data'][0]['message'] == 'is too long (maximum is 500 characters)'


# fail in test case we assumed that it would cause an error
def test_edit_post_not_by_author():
    response = simple_utils.create_request("edit_post_not_by_author",
                                        "posts" + "/" + str(simple_utils.use_existing_id("posts")), "PATCH")
    assert response['code'] == 200


@pytest.mark.tc28
def test_anonymous_get_request():
    response = simple_utils.anonymous_get_request("posts")
    print(response['json'])
    assert response['code'] == 200
