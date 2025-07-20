from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status
from app import utils
from app.auth.auth import create_access_token
from app.utils.config import settings
from app.core.database import get_db
from app.models.tokenBlockList import TokenBlacklist
from app.models.user import User  # ✅ Import the actual model directly
from app.schemas import user_schema  # This is okay if your schemas are grouped here
from fastapi import APIRouter, Depends, Request, HTTPException
from jose import jwt, JWTError

from app.utils.utils import verify_password

router = APIRouter(tags=["Authentication"])
@router.post("/register", response_model=user_schema.UserResponse)
def register_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    hashed_pw = utils.hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.username})
    print("Generated JWT Token:", token)

    return {"access_token": token, "token_type": "bearer"}

@router.post("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = token.split(" ")[1]

    user_id = get_user_id_from_token(token)  # write a function to decode and get user_id

    db_token = TokenBlacklist(token=token, user_id=user_id)
    db.add(db_token)
    db.commit()

    return {"message": "Logged out"}


def get_user_id_from_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # Query user ID from DB
        from app.models.user import User
        from app.core.database import SessionLocal

        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        db.close()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user.id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


