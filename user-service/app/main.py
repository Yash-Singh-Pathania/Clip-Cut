from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from models import User, SessionLocal
from schemas import (
    UserCreate,
    UserOut,
    UserLogin,
    UserUpdate,
)
from password import hash_password, verify_password

# -----------------------------------------------------------------------------
# FastAPI Initialization
# -----------------------------------------------------------------------------
app = FastAPI(title="User Service API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins
    allow_credentials=True,  # Allow cookies to be sent with requests
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# -----------------------------------------------------------------------------
# Dependency to get DB session
# -----------------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------------------------------------------------------
# Helper/CRUD functions
# -----------------------------------------------------------------------------
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user with hashed password."""
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        occupation=user_data.occupation,
        hashed_password=hash_password(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@app.get("/")
def root():
    return {"message": "Welcome to the User Service API"}

@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    1. Validates that occupation is one of ("salaries", "student", "other").
    2. Ensures email is unique in DB.
    3. Hashes the password before storing.
    """
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )
    new_user = create_user(db, user_data)
    return new_user

@app.post("/login")
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    1. Checks email/password combination.
    2. Returns a simple success/failure message.
       (Real apps typically return a JWT or session token.)
    """
    user = get_user_by_email(db, login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # In real-world apps: generate and return an access token (e.g. JWT)
    return {"message": "Login successful", "user_id": user.id}

@app.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    """List all users."""
    users = db.query(User).all()
    return users

@app.get("/users/{user_id}", response_model=UserOut)
def get_user_by_id_route(user_id: int, db: Session = Depends(get_db)):
    """Get a single user by ID."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user

@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Update user details (name, occupation)."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user_data.name is not None:
        user.name = user_data.name
    if user_data.occupation is not None:
        user.occupation = user_data.occupation
    
    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user by ID."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
