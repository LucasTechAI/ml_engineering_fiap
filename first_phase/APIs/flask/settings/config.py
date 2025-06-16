class Config:
    """
    Configurações da aplicação Flask.

    Attributes:
        SECRET_KEY (str): Chave secreta usada pelo Flask para sessões e segurança.
        CACHE_TYPE (str): Tipo de cache utilizado pela aplicação (ex: 'simple').
        SWAGGER (dict): Configurações para a documentação Swagger UI.
        SQLALCHEMY_DATABASE_URI (str): URI de conexão do banco de dados SQLAlchemy.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Flag para desabilitar o monitoramento de modificações no SQLAlchemy.
        JWT_SECRET_KEY (str): Chave secreta usada para assinatura dos tokens JWT.
    """

    SECRET_KEY = 'your_secret_key_here'
    CACHE_TYPE = 'simple'
    SWAGGER = {
        'title': 'Catálogo de Receitas',
        'uiversion': 3
    }
    SQLALCHEMY_DATABASE_URI = 'sqlite:///recipes.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your_jwt_secret_key_here'
