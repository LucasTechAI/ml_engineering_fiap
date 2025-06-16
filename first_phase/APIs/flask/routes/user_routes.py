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
        current_user: Optional[str] = get_jwt_identity()
        logger.info(f"Protected route accessed by user: {current_user}")
        return jsonify(logged_in_as=current_user), 200
