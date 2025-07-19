from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import user_routes
from app.routes import auth

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend URL
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


# app.include_router(user.router, prefix="/api/users", tags=["Users"])


@app.get("/api/protected")
def protected_route():
    return {"message": "You are authenticated!"}

app.include_router(user_routes.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
