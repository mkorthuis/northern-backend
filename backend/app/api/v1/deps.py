from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.core.db import engine

def get_db() -> Generator[Session, None, None]:
    """
    Create a new database session and ensure it's closed properly.
    
    This dependency guarantees that the session is closed and connection 
    is returned to the pool after the request is processed, even if an 
    exception occurs.
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

SessionDep = Annotated[Session, Depends(get_db)]
