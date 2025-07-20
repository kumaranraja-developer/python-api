from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from app import utils

from requests import Session
import uuid
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.user import User
from app.utils.config import settings
from app.utils.utils import is_token_blacklisted


def authenticate_user(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # You can later replace this with real JWT logic
    return {
        "access_token": "dummy-token",
        "token_type": "bearer",
        "user": user.username
    }


def get_current_user(
        request: Request, db: Session = Depends(get_db)
) -> User:
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = token.split(" ")[1]

    # 🔒 Check blacklist
    if is_token_blacklisted(token, db):
        raise HTTPException(status_code=401, detail="Token has been revoked")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4())  # required for blacklist
    })
    encoded_jwt = jwt.encode(to_encode, "your-secret", algorithm="HS256")
    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
