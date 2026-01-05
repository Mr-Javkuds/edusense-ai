from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# CONFIG
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY tidak ditemukan! "
        "Pastikan file .env ada dan berisi SECRET_KEY. "
        "Copy dari .env.example jika belum ada."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Setup Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Setup skema ambil token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- FUNGSI BANTUAN ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    
    # [PERBAIKAN DI SINI]
    # Menggunakan datetime.utcnow() agar format waktunya benar untuk JWT
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Encode jadi JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- MIDDLEWARE UTAMA (DEPENDENCY) ---
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau kadaluwarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None or role is None:
            raise credentials_exception
            
        return {"username": username, "role": role}
    except JWTError:
        raise credentials_exception

# --- ROLE CHECKER ---
class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: dict = Depends(get_current_user)):
        if user["role"] not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Akses Ditolak! Khusus role: {self.allowed_roles}"
            )
        return user