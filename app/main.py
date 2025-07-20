from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.auth.auth import get_current_user
from app.core.database import Base, engine
from app.routes import user_routes
from app.routes import auth_routes
from fastapi import Depends

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables
Base.metadata.create_all(bind=engine)
@app.get("/")
def read_root():
    print("hello world")
    return {"message": "Hello World"}


@app.get("/api/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "Authorized", "user": current_user}

app.include_router(user_routes.router, prefix="/api")
app.include_router(auth_routes.router, prefix="/api")

