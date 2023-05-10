
def validate(psw: str): 
    """
    Function for validiting password
    """
    # Check minimum length
    if len(psw) < 8:
        return False, "Password is too short!"
    
    # Check for uppercase and lowercase characters
    has_uppercase = False
    has_lowercase = False
    for char in psw:
        if char.isupper():
            has_uppercase = True
        elif char.islower():
            has_lowercase = True
    
    if not has_uppercase or not has_lowercase:
        return False, "No uppercase or lowercase characters!"
    
    # Check for digits
    has_digit = False
    for char in psw:
        if char.isdigit():
            has_digit = True
            break
    
    if not has_digit:
        return False, "No digits!" 
    
    # Check for special characters
    has_special_char = False
    special_characters = "!@#$%^&*()-=_+[]{}|;:,.<>/?"
    for char in psw:
        if char in special_characters:
            has_special_char = True
            break
    
    if not has_special_char:
        return False, "No special characters!"
    
    # Password meets all criteria
    return True, ""