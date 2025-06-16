from sqlalchemy.orm import Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
from typing import Any

db = SQLAlchemy()

class BaseModel(db.Model):
    """
    Classe base abstrata para todos os modelos, com campo `id` como chave primária.

    Attributes:
        id (int): Identificador único do registro.
    """
    __abstract__ = True
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    def __init__(self, **kwargs: Any) -> None:
        """
        Inicializa o modelo com os argumentos passados.
        """
        super().__init__(**kwargs)

class User(BaseModel):
    """
    Modelo para representar usuários.

    Attributes:
        username (str): Nome único do usuário.
        password (str): Hash da senha do usuário.
    """
    __tablename__ = 'user'
    username: Mapped[str] = mapped_column(db.String(80), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(120), nullable=False)

class Recipe(BaseModel):
    """
    Modelo para representar receitas culinárias.

    Attributes:
        title (str): Título da receita.
        ingredients (str): Ingredientes necessários para a receita.
        time_minutes (int): Tempo estimado de preparo em minutos.
    """
    __tablename__ = 'recipe'
    title: Mapped[str] = mapped_column(db.String(120), nullable=False)
    ingredients: Mapped[str] = mapped_column(db.Text, nullable=False)
    time_minutes: Mapped[int] = mapped_column(db.Integer, nullable=False)
