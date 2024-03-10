from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from schemas import UserCreate, UserUpdate
from models import User as DBUser
from database import get_db
from fastapi import APIRouter



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Using the get_secret function to get SECRET_KEY and ALGORITHM
SECRET_KEY = get_secret("MyAppSecretKey")  # Placeholder function call for demonstration
ALGORITHM = get_secret("MyAppAlgorithm")  # Placeholder function call for demonstration

# Token expiration time
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Token model for response
class Token(BaseModel):
    access_token: str
    token_type: str
    id: int

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Model to hold token data
class TokenData(BaseModel):
    email: Optional[str] = None

# Function to create JWT token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency to get current user based on token
async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(DBUser).filter(DBUser.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

# Endpoint for user signup
@router.post("/signup", response_model=UserUpdate)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Additional error handling and validations can be implemented here
    hashed_password = pwd_context.hash(user.password)
    db_user = DBUser(email=user.email, hashed_password=hashed_password,
                     first_name=user.first_name, last_name=user.last_name, company_name=user.company_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Endpoint for user login and token generation
@router.post("/login", response_model=Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(DBUser).filter(DBUser.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "id": user.id}

# Example protected endpoint that requires authentication
@router.get("/homepage")
async def read_homepage(current_user: DBUser = Depends(get_current_user)):
    return {"Welcome": current_user.first_name}

# Endpoint to fetch user details by ID
@router.get("/user/{user_id}", response_model=UserUpdate)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
