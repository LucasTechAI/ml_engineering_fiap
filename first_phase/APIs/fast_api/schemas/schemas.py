from pydantic import BaseModel
from typing import Optional

class UserRegister(BaseModel):
    """
    Schema for user registration.
    Contains fields for username and password.
    
    Attributes:
        username (str): The username for the new user.
        password (str): The password for the new user.
    """

    username: str
    password: str

class UserLogin(BaseModel):
    """
    Schema for user login.
    Contains fields for username and password.
    Attributes:
        username (str): The username of the user logging in.
        password (str): The password of the user logging in.
    """
    username: str
    password: str

class RecipeCreate(BaseModel):
    """
    Schema for creating a new recipe.
    Contains fields for the recipe title, ingredients, and preparation time.
    Attributes:
        title (str): The title of the recipe.
        ingredients (str): The ingredients required for the recipe.
        time_minutes (int): The preparation time in minutes.
    """
    title: str
    ingredients: str
    time_minutes: int

class RecipeUpdate(BaseModel):
    """
    Schema for updating an existing recipe.
    Contains optional fields for the recipe title, ingredients, and preparation time.
    Attributes:
        title (Optional[str]): The new title of the recipe.
        ingredients (Optional[str]): The new ingredients for the recipe.
        time_minutes (Optional[int]): The new preparation time in minutes.
    """
    title: Optional[str]
    ingredients: Optional[str]
    time_minutes: Optional[int]

class RecipeOut(BaseModel):
    """
    Schema for outputting recipe details.
    Contains fields for the recipe ID, title, ingredients, and preparation time.
    Attributes:
        id (int): The unique identifier of the recipe.
        title (str): The title of the recipe.
        ingredients (str): The ingredients required for the recipe.
        time_minutes (int): The preparation time in minutes.
    """
    id: int
    title: str
    ingredients: str
    time_minutes: int

    class Config:
        """
        Configuration for the RecipeOut schema.
        Enables ORM mode to allow compatibility with SQLAlchemy models.
        """
        orm_mode = True
