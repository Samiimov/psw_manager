import pytest
import main

@pytest.fixture(scope='session')
def app():
    main.mongo.create_connection()
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

def test_login_get(app):
    response = app.get('/login')
    assert response.status_code == 200

def test_vault_creation_post_success(app):
    response = app.post("/signin", data={
        "username": "testi2323A!!",
        "password": "testi2323A!!"
    }, follow_redirects=True)

    assert "User was created successfully!" in response.text

    response = app.post("/login", data={
        "username": "testi2323A!!",
        "password": "testi2323A!!"
    }, follow_redirects=True)
    
    response = app.post("/create_vault", data={
        "Name": "TestVault"
    }, follow_redirects=True)
    assert "Vault created sucessfully" in response.text

def test_vault_creation_post_already_exists(app):
    response = app.post("/login", data={
        "username": "testi2323A!!",
        "password": "testi2323A!!"
    }, follow_redirects=True)
    
    response = app.post("/create_vault", data={
        "Name": "TestVault"
    }, follow_redirects=True)
    assert "already exists!" in response.text

def test_vault_creation_post_cant_be_empty(app):
    response = app.post("/login", data={
        "username": "testi2323A!!",
        "password": "testi2323A!!"
    }, follow_redirects=True)
    
    response = app.post("/create_vault", data={
        "Name": ""
    }, follow_redirects=True)
    assert " be empty or end in space!" in response.text

def test_update_vault_post_success(app):
    response = app.post("/login", data={
        "username": "testi2323A!!",
        "password": "testi2323A!!"
    }, follow_redirects=True)
    
    response = app.post("/update_vault/TestVault", data={
        "Name": ["TestiImem"],
        "Password": ["TestiSalasana123!"]
    }, follow_redirects=True)
    assert "Items saved succesfully!" in response.text

def test_update_vault_post_fail_to_update(app):
    response = app.post("/login", data={
        "username": "testi2323A!!",
        "password": "testi2323A!!"
    }, follow_redirects=True)
    
    response = app.post("/update_vault/TestVault", data={
        "Name": ["TestItem1"],
        "Password": ["aaaaa"]
    }, follow_redirects=True)
    print(response.text)
    assert "Password is too short!" in response.text and "Other items saved successfully" in response.text

def test_remove_vault_success(app):
    response = app.post("/login", data={
        "username": "testi2323A!!",
        "password": "testi2323A!!"
    }, follow_redirects=True)
    
    response = app.post("/remove_vault/TestVault", follow_redirects=True)
    assert "Vault removed succesfully!" in response.text

def test_remove_vault_vault_doent_exist(app):
    response = app.post("/login", data={
        "username": "testi2323A!!",
        "password": "testi2323A!!"
    }, follow_redirects=True)
    
    response = app.post("/remove_vault/TestVault", follow_redirects=True)
    assert "Given vault doesn" in response.text
