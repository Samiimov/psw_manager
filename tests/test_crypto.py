from utils.crypto import crypto
import os
import base64

def test_key_derivation():
    salt = os.urandom(16)
    test_key_for_key_derivation = "TestKeyThisOneIs"
    key = crypto.derive_key(test_key_for_key_derivation,
                            salt)
    verify = crypto.verify(test_key_for_key_derivation,
                           key,
                           salt)
    assert verify == True

def test_encryption_and_decryption():
    salt = os.urandom(16)
    test_data = "ThisIsATestString"
    test_key_for_key_derivation = "TestKeyThisOneIs"
    key = crypto.derive_key(test_key_for_key_derivation,
                            salt)
    
    encryped_data = crypto.encrypt(key, test_data)
    decrypted_data = crypto.decrypt(key, encryped_data).decode()
    assert test_data == decrypted_data
    

     