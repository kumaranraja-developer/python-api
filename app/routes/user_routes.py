from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User  # ✅ Import the actual model directly
from app.schemas import schemas  # This is okay if your schemas are grouped here

router = APIRouter()

@router.get("/users", response_model=list[schemas.UserResponse])
def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()
