def normalize_phone_number(phone_number: str) -> str:
    phone_number = phone_number.strip()

    if phone_number.startswith("+98"):
        phone_number = "0" + phone_number[3:]
    elif phone_number.startswith("0098"):
        phone_number = "0" + phone_number[4:]
    elif phone_number.startswith("98") and len(phone_number) == 12:
        phone_number = "0" + phone_number[2:]
    elif phone_number.startswith("9") and len(phone_number) == 10:
        phone_number = "0" + phone_number

    return phone_number
