import random
import string


def generate_invite_code() -> str:
    letters = "".join(random.choices(string.ascii_uppercase, k=4))
    digits = "".join(random.choices(string.digits, k=4))
    return f"{letters}-{digits}"
