from pydantic import BaseModel

class Settings(BaseModel):
    authjwt_secret_key: str = "your-jwt-secret-key" 

def get_settings():
    return Settings()
