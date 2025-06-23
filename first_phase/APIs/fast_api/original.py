from fastapi import FastAPI, Depends, HTTPException, status, Query, Path
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from passlib.hash import bcrypt

# --- Configurações e Banco de Dados ---
DATABASE_URL = "sqlite:///./recipes.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, index=True, nullable=False)
    password = Column(String(200), nullable=False)

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    ingredients = Column(String(500), nullable=False)
    time_minutes = Column(Integer, nullable=False)

# --- Schemas Pydantic ---
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class RecipeCreate(BaseModel):
    title: str
    ingredients: str
    time_minutes: int

class RecipeUpdate(BaseModel):
    title: Optional[str]
    ingredients: Optional[str]
    time_minutes: Optional[int]

class RecipeOut(BaseModel):
    id: int
    title: str
    ingredients: str
    time_minutes: int

    class Config:
        orm_mode = True

# --- Config JWT ---
class Settings(BaseModel):
    authjwt_secret_key: str = "your-jwt-secret-key"  # Trocar para chave segura!

@AuthJWT.load_config
def get_config():
    return Settings()

# --- App FastAPI ---
app = FastAPI(title="Recipe API with JWT Authentication")

# --- Dependency to get DB session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Exception Handler JWT ---
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message}
    )

# --- Rotas ---

@app.post('/register', status_code=status.HTTP_201_CREATED, tags=["User"])
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = bcrypt.hash(user.password)
    new_user = User(username=user.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

@app.post('/login', tags=["User"])
def login(user: UserLogin, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not bcrypt.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}

@app.get('/protected', tags=["User"])
def protected(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    return {"logged_in_as": current_user}

@app.post('/recipes', status_code=status.HTTP_201_CREATED, tags=["Recipe"])
def create_recipe(recipe: RecipeCreate, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    new_recipe = Recipe(
        title=recipe.title,
        ingredients=recipe.ingredients,
        time_minutes=recipe.time_minutes
    )
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return {"message": "Recipe created successfully", "recipe_id": new_recipe.id}

@app.get('/recipes', response_model=List[RecipeOut], tags=["Recipe"])
def get_recipes(
    ingredients: Optional[str] = Query(None, description="Filter by ingredients substring"),
    max_time: Optional[int] = Query(None, description="Filter by max preparation time in minutes"),
    db: Session = Depends(get_db)
):
    query = db.query(Recipe)
    if ingredients:
        query = query.filter(Recipe.ingredients.contains(ingredients))
    if max_time is not None:
        query = query.filter(Recipe.time_minutes <= max_time)
    return query.all()

@app.put('/recipes/{recipe_id}', tags=["Recipe"])
def update_recipe(
    recipe_id: int = Path(..., description="ID da receita a ser atualizada"),
    recipe: RecipeUpdate = None,
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)
):
    Authorize.jwt_required()
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if not recipe or not any([recipe.title, recipe.ingredients, recipe.time_minutes]):
        raise HTTPException(status_code=400, detail="No data provided for update")

    if recipe.title is not None:
        db_recipe.title = recipe.title
    if recipe.ingredients is not None:
        db_recipe.ingredients = recipe.ingredients
    if recipe.time_minutes is not None:
        db_recipe.time_minutes = recipe.time_minutes

    db.commit()
    return {"message": "Recipe updated successfully"}

@app.delete('/recipes/{recipe_id}', tags=["Recipe"])
def delete_recipe(
    recipe_id: int = Path(..., description="ID da receita a ser deletada"),
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)
):
    Authorize.jwt_required()
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db.delete(db_recipe)
    db.commit()
    return {"message": "Recipe deleted successfully"}

# --- Inicialização do banco ---
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
