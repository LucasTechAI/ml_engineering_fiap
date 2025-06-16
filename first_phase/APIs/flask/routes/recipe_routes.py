from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required
from models.models import Recipe, db
from typing import Tuple
import logging

logger = logging.getLogger(__name__)
recipe_bp = Blueprint('recipes', __name__, url_prefix='/recipes')


@recipe_bp.route('/', methods=['POST'])
@jwt_required()
def create_recipe() -> Tuple[Response, int]:
    logger.info("Request to create recipe received")
    data = request.get_json()
    if not data or not all(k in data for k in ('title', 'ingredients', 'time_minutes')):
        logger.warning("Invalid input data for creating recipe")
        return jsonify({"message": "Invalid input data"}), 400
    try:
        new_recipe = Recipe(
            title=data['title'],
            ingredients=data['ingredients'],
            time_minutes=int(data['time_minutes'])
        )
        db.session.add(new_recipe)
        db.session.commit()
        logger.info(f"Recipe created successfully: {new_recipe.title}")
        return jsonify({"message": "Recipe created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating recipe: {e}")
        return jsonify({"message": f"Error creating recipe: {str(e)}"}), 400


@recipe_bp.route('/', methods=['GET'])
def get_recipes() -> Tuple[Response, int]:
    logger.info("Request to retrieve recipes received")
    ingredients = request.args.get('ingredients')
    max_time = request.args.get('max_time', type=int)
    query = Recipe.query
    if ingredients:
        query = query.filter(Recipe.ingredients.contains(ingredients))
        logger.info(f"Filtering recipes by ingredients containing: {ingredients}")
    if max_time is not None:
        query = query.filter(Recipe.time_minutes <= max_time)
        logger.info(f"Filtering recipes by max_time <= {max_time}")
    recipes = query.all()
    logger.info(f"Found {len(recipes)} recipes matching filters")
    return jsonify([
        {
            'id': recipe.id,
            'title': recipe.title,
            'ingredients': recipe.ingredients,
            'time_minutes': recipe.time_minutes
        } for recipe in recipes
    ]), 200


@recipe_bp.route('/<int:recipe_id>', methods=['PUT'])
@jwt_required()
def update_recipe(recipe_id: int) -> Tuple[Response, int]:
    logger.info(f"Request to update recipe id {recipe_id} received")
    data = request.get_json()
    recipe = Recipe.query.get_or_404(recipe_id)
    if not data or not any(k in data for k in ('title', 'ingredients', 'time_minutes')):
        logger.warning(f"No data provided for update on recipe id {recipe_id}")
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
                logger.info(f"Updated {field} for recipe id {recipe_id}")
            except (ValueError, TypeError):
                logger.error(f"Invalid value for {field} on recipe id {recipe_id}")
                return jsonify({"message": f"Invalid value for {field}"}), 400

    if not updated:
        logger.warning(f"No valid fields provided to update for recipe id {recipe_id}")
        return jsonify({"message": "No valid fields provided to update"}), 400
    db.session.commit()
    logger.info(f"Recipe id {recipe_id} updated successfully")
    return jsonify({"message": "Recipe updated successfully"}), 200


@recipe_bp.route('/<int:recipe_id>', methods=['DELETE'])
@jwt_required()
def delete_recipe(recipe_id: int) -> Tuple[Response, int]:
    logger.info(f"Request to delete recipe id {recipe_id} received")
    recipe = Recipe.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()
    logger.info(f"Recipe id {recipe_id} deleted successfully")
    return jsonify({"message": "Recipe deleted successfully"}), 200
