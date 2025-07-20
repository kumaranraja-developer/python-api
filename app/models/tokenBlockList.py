from sqlalchemy import Column, Integer, String, DateTime, Boolean
import datetime

from app.core.database import Base


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(512), unique=True, nullable=False)

    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expired = Column(Boolean, default=False)
