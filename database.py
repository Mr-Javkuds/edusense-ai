from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# DATABASE CONFIGURATION
# Baca dari environment variable, fallback ke default jika tidak ada
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:Code_is_fun@db.goepvlgunmauzaztipbf.supabase.co:5432/postgres"
)

# Engine Configuration untuk Supabase (Remote DB)
# - pool_pre_ping: Cek koneksi masih hidup sebelum digunakan
# - pool_recycle: Refresh koneksi setelah 5 menit (300 detik)
# - pool_size: Max koneksi di pool (Supabase free tier limit ~10)
# - max_overflow: Koneksi tambahan saat pool penuh
# - pool_timeout: Timeout untuk mendapatkan koneksi dari pool
engine = create_async_engine(
    DATABASE_URL, 
    echo=False,
    pool_pre_ping=True,        # Auto-reconnect jika koneksi mati
    pool_recycle=300,          # Recycle koneksi setiap 5 menit
    pool_size=5,               # Pool size untuk Supabase free tier
    max_overflow=10,           # Max tambahan koneksi
    pool_timeout=30,           # Timeout 30 detik
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session