from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=60)

    to_encode.update({"exp": expire})

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    print("GENERATED TOKEN:", token)

    return token