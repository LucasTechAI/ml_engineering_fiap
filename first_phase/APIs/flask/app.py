from typing import Tuple, Optional, Dict, Any
from flask import jsonify, Response
import logging

logger = logging.getLogger(__name__)

def validate_json_fields(
    data: Optional[Dict[str, Any]], 
    required_fields: list[str]
) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[Response, int]]]:
    """
    Valida se o JSON recebido contém os campos obrigatórios.

    Args:
        data (Optional[Dict[str, Any]]): Dicionário contendo os dados JSON da requisição.
        required_fields (list[str]): Lista de campos obrigatórios que devem estar presentes em `data`.

    Returns:
        Tuple[Optional[Dict[str, Any]], Optional[Tuple[Response, int]]]:
            - Primeiro elemento: o próprio `data` se válido, ou None se inválido.
            - Segundo elemento: None se válido, ou uma tupla com a resposta JSON de erro e o código HTTP 400 se inválido.

    """
    if not data:
        logger.error("Validation error: No data provided")
        return None, (jsonify({"message": "No data provided"}), 400)
    
    missing = [field for field in required_fields if field not in data]
    if missing:
        logger.error(f"Validation error: Missing fields: {missing}")
        return None, (jsonify({"message": f"Missing fields: {missing}"}), 400)

    logger.info("JSON validation passed")
    return data, None
