from fastapi import FastAPI
from routes import user_routes, recipe_routes
from models.models import Base
from database import engine
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse

api_config = {
    "title": "Recipe API",
    "description": """
            A secure and user-friendly REST API for managing users and cooking recipes.  
            Key features include:
            - JWT-based authentication
            - User registration and login
            - Create, update, list, and delete recipes
            - Filter recipes by ingredients and preparation time

            Built with FastAPI, SQLAlchemy, and SQLite for fast development and easy integration.
    """,
    "version": "1.0.0",
    "terms_of_service": "https://yourdomain.com/terms",
    "contact": {
        "name": "Lucas Mendes",
        "url": "https://yourdomain.com",
        "email": "lucas@example.com"
    },
    "license_info": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
}

app = FastAPI(**api_config)

# Criação das tabelas ao iniciar
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# Tratamento de erro JWT
@app.exception_handler(AuthJWTException)
def jwt_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.message})

# Inclusão de rotas
app.include_router(user_routes.router)
app.include_router(recipe_routes.router)
