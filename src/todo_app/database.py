from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:pyfhew-qygcAh-tigga9@127.0.0.1:3306/TodoApplicationDatabase"
SQLALCHEMY_DATABASE_URL = "sqlite:///./todo_app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
