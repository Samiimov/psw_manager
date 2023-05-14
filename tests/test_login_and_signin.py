import pytest
import main

@pytest.fixture(scope='session')
def app():
    """
    Fixture for setting up mongo test databases and changing Flask app config for testing.
    """
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
    """
    Test sing in page with GET
    """
    response = app.get('/signin')
    assert response.status_code == 200

def test_login_get(app):
    """
    Test login page with GET
    """
    response = app.get('/login')
    assert response.status_code == 200

def test_signin_post_success(app):
    """
    Test creating a new user.
    """
    response = app.post("/signin", data={
        "username": "testi2323A!!",
        "password": "testi2323A!!"
    }, follow_redirects=True)
    assert "User was created successfully!" in response.text

def test_signin_post_wrong_username(app):
    """
    Test creating a user with invalid name.
    """
    response = app.post("/signin", data={
        "username": "",
        "password": "testi"
    }, follow_redirects=True)
    assert "Username cannot be empty!" in response.text

def test_signin_post_wrong_password(app):
    """
    Test creating a user with invalid password.
    """
    response = app.post("/signin", data={
        "username": "testi",
        "password": "testi"
    }, follow_redirects=True)
    assert "Password is too short!" in response.text

def test_signin_post_taken_username(app):
    """
    Test creating user with a taken username.
    """
    response = app.post("/signin", data={
        "username": "testi2323A!!",
        "password": "testi"
    }, follow_redirects=True)
    assert "This username is taken!" in response.text

def test_login_post_success(app):
    """
    Test login with valid credentials.
    """
    response = app.post("/login", data={
        "username": "testi2323A!!",
        "password": "testi2323A!!"
    }, follow_redirects=True)
    assert "Logged In!" in response.text

def test_login_post_wrong_username(app):
    """
    Test login with username that doesn't exist.
    """
    response = app.post("/login", data={
        "username": "testi",
        "password": "testi"
    }, follow_redirects=True)
    assert "Given username doesn" in response.text

def test_login_post_wrong_password(app):
    """
    Test login with an invalid username.
    """
    response = app.post("/login", data={
        "username": "testi2323A!!",
        "password": "testi"
    }, follow_redirects=True)
    assert "Password is incorrect!" in response.text