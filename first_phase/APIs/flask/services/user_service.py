from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask import jsonify, Response
from typing import Dict, Tuple
from models import db, User


class UserService:
    @staticmethod
    def register(data: Dict[str, str]) -> Tuple[Response, int]:
        """
        Registra um novo usuário no banco de dados.

        Args:
            data (Dict[str, str]): Dicionário contendo 'username' e 'password'.

        Returns:
            Tuple[Response, int]: Resposta JSON e código HTTP.
                201 se usuário criado com sucesso,
                400 se usuário já existe.
        """
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"message": "User already exists"}), 400
        
        hashed_password = generate_password_hash(data['password'])
        user = User(username=data['username'], password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201

    @staticmethod
    def login(data: Dict[str, str]) -> Tuple[Response, int]:
        """
        Realiza o login do usuário, validando as credenciais e gerando um token JWT.

        Args:
            data (Dict[str, str]): Dicionário contendo 'username' e 'password'.

        Returns:
            Tuple[Response, int]: Resposta JSON contendo o token de acesso e código HTTP.
                200 se login bem-sucedido,
                401 se credenciais inválidas.
        """
        user = User.query.filter_by(username=data['username']).first()
        if not user or not check_password_hash(user.password, data['password']):
            return jsonify({"message": "Invalid credentials"}), 401
        
        token = create_access_token(identity=user.username)
        return jsonify(access_token=token), 200
