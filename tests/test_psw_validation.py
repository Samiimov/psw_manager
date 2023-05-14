from utils.psw_validation import validate

def test_valid_password():
    """
    Test valid password.
    """
    is_valid, reason = validate("TestiSalasana123!")
    assert is_valid

def test_too_short_password():
    """
    Test too short password
    """
    is_valid, reason = validate("aaaaa")
    assert is_valid == False and reason == "Password is too short!"

def test_no_uppercase():
    """
    Test password with no lowercase letters
    """
    is_valid, reason = validate("aaaaaaaaaa")
    assert is_valid == False and reason == "No uppercase or lowercase characters!"

def test_no_lowercase():
    """
    Test password with no uppercase letters
    """
    is_valid, reason = validate("AAAAAAAAAAAA")
    assert is_valid == False and reason == "No uppercase or lowercase characters!"

def test_no_digits():
    """
    Test password with no digits
    """
    is_valid, reason = validate("aaaaAAAA")
    assert is_valid == False and reason == "No digits!"

def test_no_special_chars():
    """
    Test password with no special chars
    """
    is_valid, reason = validate("aaaaAAAA1111")
    assert is_valid == False and reason == "No special characters!"