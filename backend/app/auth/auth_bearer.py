from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt

SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"

security = HTTPBearer()


def verify_token(
    auth: HTTPAuthorizationCredentials = Depends(security)
):

    token = auth.credentials

    print("TOKEN RECEIVED:", token)

    try:

        decoded_token = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )

        print("DECODED:", decoded_token)

        return decoded_token

    except Exception as e:

        print("JWT ERROR:", e)

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )