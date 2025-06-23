from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flasgger import Swagger
from werkzeug.security import generate_password_hash, check_password_hash

class Config:
    SECRET_KEY = 'your-secret-key'  # Troque para uma chave segura
    SQLALCHEMY_DATABASE_URI = 'sqlite:///recipes.db'  # Banco de dados SQLite local
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your-jwt-secret-key'  # Troque para uma chave segura

# Inicialização do banco (SQLAlchemy)
db = SQLAlchemy()

# Modelos
class BaseModel:
    @staticmethod
    def init_app(app):
        db.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    ingredients = db.Column(db.String(500), nullable=False)
    time_minutes = db.Column(db.Integer, nullable=False)

# Factory da aplicação
def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    BaseModel.init_app(app)
    JWTManager(app)
    Swagger(app)

    register_routes(app)

    return app

# Registro das rotas
def register_routes(app: Flask) -> None:

    @app.route('/register', methods=['POST'])
    def register_user():
        """
        Endpoint para registrar um novo usuário.
        ---
        tags:
          - User
        parameters:
          - in: body
            name: user
            description: Dados do usuário a serem registrados
            required: true
            schema:
              type: object
              properties:
                username:
                  type: string
                  example: johndoe
                password:
                  type: string
                  example: securepassword123
        responses:
          201:
            description: Usuário criado com sucesso
          400:
            description: Erro de validação ou usuário já existe
        """
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"message": "Username and password are required"}), 400
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"message": "User already exists"}), 400
        hashed_password = generate_password_hash(data['password'])
        new_user = User(username=data['username'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201

    @app.route('/login', methods=['POST'])
    def login_user():
        """
        Endpoint para autenticar um usuário e gerar um token JWT.
        ---
        tags:
          - User
        parameters:
          - in: body
            name: user
            description: Dados do usuário para autenticação
            required: true
            schema:
              type: object
              properties:
                username:
                  type: string
                  example: johndoe
                password:
                  type: string
                  example: securepassword123
        responses:
          200:
            description: Token JWT gerado com sucesso
          400:
            description: Erro de validação
          401:
            description: Credenciais inválidas
        """
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"message": "Username and password are required"}), 400
        user = User.query.filter_by(username=data['username']).first()
        if not user or not check_password_hash(user.password, data['password']):
            return jsonify({"message": "Invalid credentials"}), 401
        access_token = create_access_token(identity=user.username)
        return jsonify(access_token=access_token), 200

    @app.route('/protected', methods=['GET'])
    @jwt_required()
    def protected():
        """
        Endpoint protegido que retorna o usuário autenticado.
        ---
        tags:
          - User
        responses:
          200:
            description: Usuário autenticado retornado com sucesso
        """ 
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), 200

    @app.route('/recipes', methods=['POST'])
    @jwt_required()
    def create_recipe():
        """
        Endpoint para criar uma nova receita.
        ---
        tags:
          - Recipe
        parameters:
          - in: body
            name: recipe
            description: Dados da receita a serem criados
            required: true
            schema:
              type: object
              properties:
                title:
                  type: string
                  example: Spaghetti Carbonara
                ingredients:
                  type: string
                  example: Spaghetti, Eggs, Parmesan, Bacon, Pepper
                time_minutes:
                  type: integer
                  example: 30
        responses:
          201:
            description: Receita criada com sucesso
          400:
            description: Erro de validação ou criação da receita
        """
        data = request.get_json()
        if not data or not all(k in data for k in ('title', 'ingredients', 'time_minutes')):
            return jsonify({"message": "Invalid input data"}), 400
        try:
            new_recipe = Recipe(
                title=data['title'],
                ingredients=data['ingredients'],
                time_minutes=int(data['time_minutes'])
            )
            db.session.add(new_recipe)
            db.session.commit()
            return jsonify({"message": "Recipe created successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error creating recipe: {str(e)}"}), 400

    @app.route('/recipes', methods=['GET'])
    def get_recipes():
        """
        Endpoint para listar receitas com filtros opcionais.
        ---
        tags:
          - Recipe
        parameters:
          - in: query
            name: ingredients
            type: string
            description: Ingredientes para filtrar as receitas
          - in: query
            name: max_time
            type: integer
            description: Tempo máximo de preparo em minutos para filtrar as receitas
        responses:
          200:
            description: Lista de receitas retornada com sucesso
          400:
            description: Erro de validação ou consulta
        """
        ingredients = request.args.get('ingredients')
        max_time = request.args.get('max_time', type=int)
        query = Recipe.query
        if ingredients:
            query = query.filter(Recipe.ingredients.contains(ingredients))
        if max_time is not None:
            query = query.filter(Recipe.time_minutes <= max_time)
        recipes = query.all()
        return jsonify([
            {
                'id': recipe.id,
                'title': recipe.title,
                'ingredients': recipe.ingredients,
                'time_minutes': recipe.time_minutes
            } for recipe in recipes
        ]), 200

    @app.route('/recipes/<int:recipe_id>', methods=['PUT'])
    @jwt_required()
    def update_recipe(recipe_id):
        """
        Endpoint para atualizar uma receita existente.
        ---
        tags:
          - Recipe
        parameters:
          - in: path
            name: recipe_id
            type: integer
            required: true
            description: ID da receita a ser atualizada
          - in: body
            name: recipe
            description: Dados da receita a serem atualizados
            required: true
            schema:
              type: object
              properties:
                title:
                  type: string
                  example: Updated Spaghetti Carbonara
                ingredients:
                  type: string
                  example: Spaghetti, Eggs, Parmesan, Bacon, Pepper, Garlic
                time_minutes:
                  type: integer
                  example: 25
        responses:
          200:
            description: Receita atualizada com sucesso
          400:
            description: Erro de validação ou atualização da receita
          404:
            description: Receita não encontrada
        """
        data = request.get_json()
        recipe = Recipe.query.get_or_404(recipe_id)
        if not data or not any(k in data for k in ('title', 'ingredients', 'time_minutes')):
            return jsonify({"message": "No data provided"}), 400

        fields = {
            'title': str,
            'ingredients': str,
            'time_minutes': int
        }

        updated = False
        for field, field_type in fields.items():
            if field in data:
                try:
                    setattr(recipe, field, field_type(data[field]))
                    updated = True
                except (ValueError, TypeError):
                    return jsonify({"message": f"Invalid value for {field}"}), 400

        if not updated:
            return jsonify({"message": "No valid fields provided to update"}), 400
        db.session.commit()
        return jsonify({"message": "Recipe updated successfully"}), 200

    @app.route('/recipes/<int:recipe_id>', methods=['DELETE'])
    @jwt_required()
    def delete_recipe(recipe_id: int):
        """
        Endpoint para deletar uma receita existente.
        ---
        tags:
          - Recipe
        parameters:
          - in: path
            name: recipe_id
            type: integer
            required: true
            description: ID da receita a ser deletada
        responses:
          200:
            description: Receita deletada com sucesso
          404:
            description: Receita não encontrada
        """
        recipe = Recipe.query.get_or_404(recipe_id)
        db.session.delete(recipe)
        db.session.commit()
        return jsonify({"message": "Recipe deleted successfully"}), 200

# Execução da aplicação
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created.")
    app.run(debug=True, port=5000)
