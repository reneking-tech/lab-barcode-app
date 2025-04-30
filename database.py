# database.py

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Create the SQLite database engine
engine = create_engine('sqlite:///lab_chemicals.db')

# Create a session factory
Session = sessionmaker(bind=engine)

# Initialize the database
def init_db():
    Base.metadata.create_all(engine)
