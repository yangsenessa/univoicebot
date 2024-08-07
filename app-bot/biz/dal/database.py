from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os 


SQLALCHEMY_DATABASE_URL=os.environ.get('SQLALCHEMY_DATABASE_URL')

POOL_SIZE = 20
POOL_RECYCLE = 3600
POOL_TIMEOUT = 300
MAX_OVERFLOW = 2
CONNECT_TIMEOUT = 60


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Database():
    
    def __init__(self) -> None:
        self.connection_is_active = False
        self.engine = None
    
    def get_db_connection(self):
        if self.connection_is_active == False:
            connect_args = {"connect_timeout": CONNECT_TIMEOUT}
            try:
                self.engine = create_engine(SQLALCHEMY_DATABASE_URL,
                                            pool_size=POOL_SIZE,
                                            pool_recycle=POOL_RECYCLE,
                                            pool_timeout=POOL_TIMEOUT,
                                            max_overflow=MAX_OVERFLOW,
                                            connect_args=connect_args)
                return self.engine
            except Exception as e:
                print("Error connecting to MySQL DB:", e)
        return self.engine
    
    def get_db_session(self, engine):
        try:
            
            Session = sessionmaker(bind=engine)
            session = Session()
            return session
        except Exception as e:
            print("Error getting DB session:", e)
            return None
        
    def get_db(self):
        session = self.get_db_session(engine)
        return session











