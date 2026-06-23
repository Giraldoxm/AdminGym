import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from database import get_db
from models import SuperAdmin, Usuario

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 días

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        gym_id = payload.get("gym_id")
        if email is None or gym_id is None:
            raise credentials_exception
        email = email.strip().lower()
    except JWTError:
        raise credentials_exception

    user = db.query(Usuario).filter(Usuario.email == email, Usuario.gym_id == gym_id).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_superadmin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> SuperAdmin:
    """Análogo a get_current_user pero para el operador de la plataforma (sin gym_id).
    El JWT de superadmin lleva scope='superadmin' en vez de gym_id — esto evita que
    un token de gym sea aceptado aquí y viceversa."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        scope: str = payload.get("scope")
        if email is None or scope != "superadmin":
            raise credentials_exception
        email = email.strip().lower()
    except JWTError:
        raise credentials_exception

    admin = db.query(SuperAdmin).filter(SuperAdmin.email == email).first()
    if admin is None:
        raise credentials_exception
    return admin
