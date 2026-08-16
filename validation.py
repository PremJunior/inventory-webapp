
def validate_name(name):
    if name is None:
        return False
    
    if name.strip() == "":
        return False
    
    if not all(char.isalpha() or char == " " for char in name):
        return False
    return True



def validate_stock(stock):
    try:
        stock = int(stock)
        if stock < 0:
            return False
        return True
    except (ValueError, TypeError):
        return False

def validate_value(value):
    try:
        value = int(value)
        if value < 0:
            return False
        return True
    except(ValueError, TypeError):
        return False