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
    """
    Create a new recipe
    ---
    tags:
      - Recipes
    security:
      - jwt: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - title
              - ingredients
              - time_minutes
            properties:
              title:
                type: string
                example: "Pancakes"
              ingredients:
                type: string
                example: "Flour, Eggs, Milk"
              time_minutes:
                type: integer
                example: 15
    responses:
      201:
        description: Recipe created successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Recipe created successfully"
      400:
        description: Invalid input data or error creating recipe
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Invalid input data"
    """
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
        logger.info(f"Recipe '{new_recipe.title}' created successfully")
        return jsonify({"message": "Recipe created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating recipe: {e}")
        return jsonify({"message": f"Error creating recipe: {str(e)}"}), 400


@recipe_bp.route('/', methods=['GET'])
def get_recipes() -> Tuple[Response, int]:
    """
    Retrieve all recipes with optional filtering by ingredients and max time.
    ---
    tags:
      - Recipes
    parameters:
      - in: query
        name: ingredients
        schema:
          type: string
        description: Filter recipes by ingredients (partial match)
      - in: query
        name: max_time
        schema:
          type: integer
        description: Filter recipes by maximum time in minutes
    responses:
      200:
        description: A list of recipes matching the filters
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  title:
                    type: string
                    example: "Pancakes"
                  ingredients:
                    type: string
                    example: "Flour, Eggs, Milk"
                  time_minutes:
                    type: integer
                    example: 15
      400:
        description: Invalid query parameters
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Invalid query parameters"
    """
    logger.info("Request to retrieve recipes received")
    ingredients = request.args.get('ingredients')
    max_time = request.args.get('max_time', type=int)

    query = Recipe.query
    if ingredients:
        query = query.filter(Recipe.ingredients.contains(ingredients))
        logger.info(f"Filtering by ingredients containing: {ingredients}")
    if max_time is not None:
        query = query.filter(Recipe.time_minutes <= max_time)
        logger.info(f"Filtering by max_time <= {max_time}")

    recipes = query.all()
    logger.info(f"Found {len(recipes)} recipes")
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
    """
    Update an existing recipe by ID
    ---
    tags:
      - Recipes
    security:
      - jwt: []
    parameters:
      - in: path
        name: recipe_id
        required: true
        schema:
          type: integer
        description: The ID of the recipe to update
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              title:
                type: string
                example: "Updated Pancakes"
              ingredients:
                type: string
                example: "Flour, Eggs, Milk, Sugar"
              time_minutes:
                type: integer
                example: 20
    responses:
      200:
        description: Recipe updated successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Recipe updated successfully"
      400:
        description: Invalid input data or error updating recipe
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Invalid value for field"
      404:
        description: Recipe not found
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Recipe not found"
    """
    logger.info(f"Request to update recipe ID {recipe_id} received")
    data = request.get_json()
    recipe = Recipe.query.get_or_404(recipe_id)

    if not data or not any(k in data for k in ('title', 'ingredients', 'time_minutes')):
        logger.warning(f"No data provided to update recipe ID {recipe_id}")
        return jsonify({"message": "No data provided"}), 400

    fields = {
        'title': str,
        'ingredients': str,
        'time_minutes': int
    }

    updated = False
    for field, cast in fields.items():
        if field in data:
            try:
                setattr(recipe, field, cast(data[field]))
                logger.info(f"Field '{field}' updated for recipe ID {recipe_id}")
                updated = True
            except (ValueError, TypeError):
                logger.error(f"Invalid value for '{field}' in recipe ID {recipe_id}")
                return jsonify({"message": f"Invalid value for {field}"}), 400

    if not updated:
        logger.warning(f"No valid fields provided to update for recipe ID {recipe_id}")
        return jsonify({"message": "No valid fields provided to update"}), 400

    db.session.commit()
    logger.info(f"Recipe ID {recipe_id} updated successfully")
    return jsonify({"message": "Recipe updated successfully"}), 200


@recipe_bp.route('/<int:recipe_id>', methods=['DELETE'])
@jwt_required()
def delete_recipe(recipe_id: int) -> Tuple[Response, int]:
    """
    Delete a recipe by ID
    ---
    tags:
      - Recipes
    security:
      - jwt: []
    parameters:
      - in: path
        name: recipe_id
        required: true
        schema:
          type: integer
        description: The ID of the recipe to delete
    responses:
      200:
        description: Recipe deleted successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Recipe deleted successfully"
      404:
        description: Recipe not found
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Recipe not found"
      400:
        description: Error deleting recipe
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Error deleting recipe"
    """
    logger.info(f"Request to delete recipe ID {recipe_id} received")
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        db.session.delete(recipe)
        db.session.commit()
        logger.info(f"Recipe ID {recipe_id} deleted successfully")
        return jsonify({"message": "Recipe deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting recipe ID {recipe_id}: {e}")
        return jsonify({"message": "Error deleting recipe"}), 400
