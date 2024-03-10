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
SECRET_KEY = get_secret("MyAppSecretKey")
ALGORITHM = get_secret("MyAppAlgorithm")

SECRET_KEY = "KPoxgJcIgMnD2I-v4kZ1fzXsAhGDYll7AyVQX9RAU1Y" 
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30



class Token(BaseModel):
    access_token: str
    token_type: str
    id: int

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class TokenData(BaseModel):
    email: str = None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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

@router.post("/signup", response_model=UserUpdate)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        if user.password != user.repeat_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
        hashed_password = pwd_context.hash(user.password)
        db_user = DBUser(email=user.email, hashed_password=hashed_password, first_name=user.first_name, last_name=user.last_name, company_name=user.company_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
    print(f"User ID: {user.id}")  # Add this line
    return {"access_token": access_token, "token_type": "bearer", "id": user.id}


@router.get("/homepage")
async def read_homepage(current_user: DBUser = Depends(get_current_user)):
    return {"Welcome": current_user.first_name}

@router.get("/user/{user_id}", response_model=UserUpdate)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user