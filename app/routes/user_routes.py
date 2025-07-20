from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app.auth.auth import get_current_user
from app.core.database import get_db
from app.models.user import User  # ✅ Import the actual model directly
from app.schemas import user_schema  # This is okay if your schemas are grouped here
from app.schemas.user_schema import UserResponse

router = APIRouter()

@router.get("/users", response_model=list[user_schema.UserResponse])
def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
