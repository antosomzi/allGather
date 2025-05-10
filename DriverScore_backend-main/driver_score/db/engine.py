from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from driver_score.settings import settings

db_engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

Base = declarative_base()


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
