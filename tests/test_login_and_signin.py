import pytest
import main

@pytest.fixture(scope='session')
def app():
    main.mongo.create_connection()
    # Change mongo collections
    main.mongo.credentials_collection = main.mongo.psw_manager_database["credentials_test"]
    main.mongo.vaults_collection = main.mongo.psw_manager_database["vaults_test"]
    main.mongo.salts_collection = main.mongo.psw_manager_database["salts_test"]
    # Empty test collections
    main.mongo.credentials_collection.delete_many({})
    main.mongo.vaults_collection.delete_many({})
    main.mongo.salts_collection.delete_many({})
    app_ = main.app
    app_.config["TESTING"] = True
    app_.config['WTF_CSRF_METHODS'] = []
    client = main.app.test_client()
    return client

def test_signin_get(app):
    response = app.get('/signin')
    assert response.status_code == 200

def test_login_get(app):
    response = app.get('/login')
    assert response.status_code == 200

def test_signin_post_success(app):
    response = app.post("/signin", data={
        "username": "testi2323A!!",
        "password": "testi2323A!!"
    }, follow_redirects=True)
    assert "User was created successfully!" in response.text

def test_signin_post_wrong_username(app):
    response = app.post("/signin", data={
        "username": "",
        "password": "testi"
    }, follow_redirects=True)
    assert "Username cannot be empty!" in response.text

def test_signin_post_wrong_password(app):
    response = app.post("/signin", data={
        "username": "testi",
        "password": "testi"
    }, follow_redirects=True)
    assert "Password is too short!" in response.text

def test_signin_post_taken_username(app):
    response = app.post("/signin", data={
        "username": "testi2323A!!",
        "password": "testi"
    }, follow_redirects=True)
    assert "This username is taken!" in response.text

def test_login_post_success(app):
    # Create user
    response = app.post("/signin", data={
        "username": "testi2323A!!",
        "password": "testi2323A!!"
    }, follow_redirects=True)

    response = app.post("/login", data={
        "username": "testi2323A!!",
        "password": "testi2323A!!"
    }, follow_redirects=True)
    assert "Logged In!" in response.text

def test_login_post_wrong_username(app):
    response = app.post("/login", data={
        "username": "testi",
        "password": "testi"
    }, follow_redirects=True)
    assert "Given username doesn" in response.text

def test_login_post_wrong_password(app):
    response = app.post("/login", data={
        "username": "testi2323A!!",
        "password": "testi"
    }, follow_redirects=True)
    assert "Password is incorrect!" in response.text