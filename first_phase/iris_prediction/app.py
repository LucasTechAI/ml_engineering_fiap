from fastapi import FastAPI
from routes.iris_routes import router as iris_router
from routes.auth_routes import router as auth_router
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from database import Base, engine

app = FastAPI(
    title="Iris Prediction API",
    version="1.0.0",
    description="""
API para predição de espécies de Íris usando Random Forest.

**Funcionalidades:**

- Registro e autenticação de usuários com JWT
- Endpoint de predição da espécie de Íris
- Armazenamento dos logs de predição no banco SQLite
- Cache em memória para melhorar performance

Use o token JWT obtido no login para acessar as rotas protegidas.
""",
    terms_of_service="https://example.com/terms/",
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)


# Cria as tabelas no SQLite
Base.metadata.create_all(bind=engine)

# Inclui rotas
app.include_router(auth_router, prefix="/users", tags=["Users"])
app.include_router(iris_router, prefix="/iris", tags=["Iris"])

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())

@app.get("/")
def root():
    return {"message": "API Iris Prediction com JWT, Cache e SQLite rodando"}
