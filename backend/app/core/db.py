from sqlmodel import create_engine
from sqlalchemy.pool import QueuePool

from app.core.config import settings

# Configure the engine with appropriate pool settings to avoid connection exhaustion
# For Heroku with 4 workers, use pool_size=2 and max_overflow=3, totaling max 5 connections per worker
# Total max connections for 4 workers: 20 connections
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    poolclass=QueuePool,
    pool_size=2,
    max_overflow=3,
    pool_timeout=30,
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=1800,   # Recycle connections after 30 minutes
)