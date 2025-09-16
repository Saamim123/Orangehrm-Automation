# utilities/random_data.py
from typing import Optional, Tuple, Dict
import secrets, string
from faker import Faker

faker = Faker()

def first_name() -> str:
    return faker.first_name()

def middle_name() -> str:
    return faker.first_name()

def last_name() -> str:
    return faker.last_name()

def employee_id(length:int=6, allow_leading_zero:bool=False) -> str:
    rng = secrets.SystemRandom()
    if allow_leading_zero:
        return ''.join(rng.choice(string.digits) for _ in range(length))
    first = rng.choice('123456789')
    rest = ''.join(rng.choice(string.digits) for _ in range(length-1)) if length>1 else ''
    return first + rest

def username_from_name(first:str, middle:Optional[str], last:str, length:int=8) -> str:
    base = (first + (middle or '') + last).lower()
    base = ''.join(ch for ch in base if ch.isalpha())
    return (base[:length]).ljust(length, 'x')  # pad if short

def password(length:int=12,
             min_upper:int=1, min_lower:int=1, min_digits:int=1, min_special:int=1,
             specials="!@#$%") -> str:
    # implement as in your big utility; keep small here for example
    import random
    pool = (random.choices(string.ascii_uppercase, k=min_upper) +
            random.choices(string.ascii_lowercase, k=min_lower) +
            random.choices(string.digits, k=min_digits) +
            random.choices(specials, k=min_special))
    remaining = length - len(pool)
    pool += random.choices(string.ascii_letters + string.digits + specials, k=remaining)
    random.shuffle(pool)
    return ''.join(pool)

def generate_employee_with_credentials(id_length=6, username_length=8, password_length=12) -> Dict:
    f = first_name(); m = middle_name(); l = last_name()
    eid = employee_id(length=id_length)
    uname = username_from_name(f, m, l, length=username_length)
    pwd = password(length=password_length)
    return {
        "first_name": f, "middle_name": m, "last_name": l,
        "employee_id": eid, "username": uname, "password": pwd, "confirm_password": pwd
    }
