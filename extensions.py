from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Define the base for declarative models
class Base(DeclarativeBase):
    pass

# Create the database instance. It will be initialized with the app in the factory.
db = SQLAlchemy(model_class=Base)
