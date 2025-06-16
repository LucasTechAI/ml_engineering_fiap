from flask_jwt_extended import jwt_required, get_jwt_identity
from validators.request_validator import validate_json_fields
from flask import request, jsonify, Flask, Response
from services.user_service import UserService
from typing import Tuple, Optional
import logging


logger = logging.getLogger(__name__)

def register_user_routes(app: Flask) -> None:

    @app.route('/register', methods=['POST'])
    def register_user() -> Tuple[Response, int]:
        """
        Register a new user
        ---
        tags:
            - Users
        requestBody:
            required: true
            content:
                application/json:
                    schema:
                        type: object
                        required:
                            - username
                            - password
                        properties:
                            username:
                                type: string
                                example: "john_doe"
                            password:
                                type: string
                                example: "securepassword123"
        responses:
            201:
                description: User registered successfully
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                message:
                                    type: string
                                    example: "User registered successfully"
            400:
                description: Invalid input data or error registering user
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                message:
                                    type: string
                                    example: "Invalid input data or error registering user"
        """
        logger.info("Register user request received")
        data, error = validate_json_fields(request.get_json(), ['username', 'password'])
        if error:
            logger.warning("Register user validation failed")
            return error
        response = UserService.register(data)
        logger.info("User registered successfully")
        return response

    @app.route('/login', methods=['POST'])
    def login_user() -> Tuple[Response, int]:
        """
        Login an existing user
        ---
        tags:
            - Users
        requestBody:
            required: true
            content:
                application/json:
                    schema:
                        type: object
                        required:
                            - username
                            - password
                        properties:
                            username:
                                type: string
                                example: "john_doe"
                            password:
                                type: string
                                example: "securepassword123"
        responses:
            200:
                description: User logged in successfully
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                access_token:
                                    type: string
                                    example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            400:
                description: Invalid input data or error logging in user
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                message:
                                    type: string
                                    example: "Invalid input data or error logging in user"
        """
        logger.info("Login user request received")
        data, error = validate_json_fields(request.get_json(), ['username', 'password'])
        if error:
            logger.warning("Login validation failed")
            return error
        response = UserService.login(data)
        logger.info("User logged in successfully")
        return response

    @app.route('/protected', methods=['GET'])
    @jwt_required()
    def protected() -> Tuple[Response, int]:
        """
        Protected route that requires a valid JWT token
        ---
        tags:
            - Users
        security:
            - jwt: []
        responses:
            200:
                description: Access granted to protected route
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                logged_in_as:
                                    type: string
                                    example: "john_doe"
            401:
                description: Unauthorized access, invalid or missing JWT token
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                message:
                                    type: string
                                    example: "Missing or invalid JWT token"
        """
        current_user: Optional[str] = get_jwt_identity()
        logger.info(f"Protected route accessed by user: {current_user}")
        return jsonify(logged_in_as=current_user), 200
