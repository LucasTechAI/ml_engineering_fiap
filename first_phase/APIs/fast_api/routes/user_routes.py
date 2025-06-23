from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from models.models import User
from schemas.schemas import UserRegister, UserLogin
from settings.config import get_settings
from passlib.hash import bcrypt
from database import get_db

router = APIRouter(tags=["User"])

@AuthJWT.load_config
def load_config():
    return get_settings()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="User already exists")
    hashed = bcrypt.hash(user.password)
    db.add(User(username=user.username, password=hashed))
    db.commit()
    return {"message": "User created successfully"}

@router.post("/login")
def login(user: UserLogin, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not bcrypt.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}

@router.get("/protected")
def protected(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return {"logged_in_as": Authorize.get_jwt_subject()}
