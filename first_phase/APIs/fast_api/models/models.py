from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    """
    User model for the application.
    Represents a user with a unique username and a hashed password.
    Attributes:
        id (int): Unique identifier for the user.
        username (str): Unique username for the user.
        password (str): Hashed password for the user.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, index=True, nullable=False)
    password = Column(String(200), nullable=False)

class Recipe(Base):
    """
    Recipe model for the application.
    Represents a recipe with a title, ingredients, and preparation time.
    Attributes:
        id (int): Unique identifier for the recipe.
        title (str): Title of the recipe.
        ingredients (str): Ingredients required for the recipe.
        time_minutes (int): Preparation time in minutes.
    """
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    ingredients = Column(String(500), nullable=False)
    time_minutes = Column(Integer, nullable=False)
