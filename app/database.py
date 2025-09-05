from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

"""
Understanding the modules and libraries
- create_engine: create connection between python and the database. Connect and send sql commands to postgreSQL
- declarative_base: classes recognized as tables
- sessionmaker: create objects to use in queries
"""

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() # Make Python classes be tables in the database

"""
Understanding the arguments inside sessionmaker
- autocommit=False : you need to call 'session.commit()' instead of confirming automatically
- autoflush=False : you need to call 'ssession.flush()' to send changes before doing queries
- bind=engine : associate 'Session' with 'engine'
"""