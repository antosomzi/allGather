from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from driver_score.settings import settings

# Create SQLAlchemy engine
db_engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

# Single declarative base for all models
Base = declarative_base()


@contextmanager
def get_db_session():
    """
    Context manager to obtain a database session.
    Automatically handles transactions and session closing.
    
    Usage:
        with get_db_session() as session:
            # Database operations
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db():
    """
    Generator to obtain a database session.
    For use with FastAPI as a dependency.
    
    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()