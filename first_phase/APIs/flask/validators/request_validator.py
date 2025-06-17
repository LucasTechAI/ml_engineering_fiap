from typing import Optional, Dict, Any, Tuple, List
from flask import jsonify, Response
import logging

logger = logging.getLogger(__name__)

def validate_json_fields(
    data: Optional[Dict[str, Any]], 
    required_fields: List[str]
) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[Response, int]]]:
    """
    Valida se o JSON recebido contém os campos obrigatórios.

    Args:
        data (Optional[Dict[str, Any]]): Dados JSON da requisição a serem validados.
        required_fields (List[str]): Lista de campos obrigatórios que devem existir em `data`.

    Returns:
        Tuple[Optional[Dict[str, Any]], Optional[Tuple[Response, int]]]:  
        Retorna os dados validados e None se sucesso,  
        ou None e uma resposta JSON com erro e código HTTP se falha na validação.
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
