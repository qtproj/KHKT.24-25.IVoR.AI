import re 

def classify(plate: str) -> str:
    """
    Classify the license plate.
    """
    # List series elements of 50cc
    firstChar50 = frozenset("ABCDEFGHKLMNPSTUVXYZ")  # List 1
    secondChar50 = frozenset("ABCEFHKLMNPRSTUVXYZ")  # List 2

    # List series elements of 100cc
    firstChar100 = frozenset("BCDEFGHKLMNPSTUVXYZ")  # List 1
    secondChar100 = set("123456789")  # List 2

    plate = re.sub(r'[^A-Za-z0-9]', '', plate)

    if len(plate) < 8 or len(plate) > 9:
        # If the plate is too short, it's invalid
        return False

    prefix = plate[:2]
    series = plate[2:4]  # Extract series (3rd and 4th characters)
    number = plate[4:]   # Extract remaining digits

    if len(series) != 2 or not number.isdigit() or not prefix.isdigit() or len(number) < 4:
        # If series doesn't have exactly 2 characters or number isn't numeric, it's invalid
        return "invalid"

    # Check if the series characters are valid
    if series[0] in firstChar50 and series[1] in secondChar50:
        return "50cc"
    if series[0] in firstChar100 and series[1] in secondChar100:  
        return "100cc"