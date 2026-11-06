
def validate_name(name):
    if name is None:
        return False
    
    if name.strip() == "":
        return False
    
    if not all(char.isalpha() or char == " " for char in name):
        return False
    return True

def _is_non_negative_integer(value):
    """Return whether a value can be stored as a non-negative whole number."""
    try:
        return int(value) >= 0
    except (ValueError, TypeError):
        return False


def validate_stock(stock):
    return _is_non_negative_integer(stock)


def validate_value(value):
    return _is_non_negative_integer(value)

def validate_email(email):
    if not isinstance(email, str):
        return False
    email = email.strip()

    if email.count("@") != 1:
        return False

    local_part, domain = email.split("@")
    return bool(local_part) and "." in domain and not domain.startswith(".")