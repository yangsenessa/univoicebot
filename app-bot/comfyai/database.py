from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


#SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://mixlab:mixlab@host.docker.internal:3306/standard?charset=utf8"
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://mixlabdb:mixlab_DB@mixlib-mid-gw.rwlb.rds.aliyuncs.com/mixlabdb?charset=utf8"
POOL_SIZE = 20
POOL_RECYCLE = 3600
POOL_TIMEOUT = 150
MAX_OVERFLOW = 2
CONNECT_TIMEOUT = 60

#SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://mixlab:mixlab@127.0.0.1:3306/standard?charset=utf8"
# SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db_connection():
    connection = mysql.connector.connect(
        host='mixlab_DB@mixlib-mid-gw.rwlb.rds.aliyuncs.com',
       # port=3306,
        user="mixlabdb",
        password="mixlab_DB",
        database="mixlabdb"
    )
    return connection

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











