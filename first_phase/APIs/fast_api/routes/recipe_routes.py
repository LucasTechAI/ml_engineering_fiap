from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from models.models import Recipe
from schemas.schemas import RecipeCreate, RecipeUpdate, RecipeOut
from typing import List, Optional
from database import get_db

router = APIRouter(prefix="/recipes", tags=["Recipe"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    new_recipe = Recipe(**recipe.dict())
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return {"message": "Recipe created successfully", "recipe_id": new_recipe.id}

@router.get("", response_model=List[RecipeOut])
def list_recipes(
        ingredients: Optional[str] = Query(None),
        max_time: Optional[int] = Query(None),
        db: Session = Depends(get_db)
    ):
    query = db.query(Recipe)
    if ingredients:
        query = query.filter(Recipe.ingredients.contains(ingredients))
    if max_time:
        query = query.filter(Recipe.time_minutes <= max_time)
    return query.all()

@router.put("/{recipe_id}")
def update_recipe(
        recipe_id: int,
        recipe: RecipeUpdate,
        db: Session = Depends(get_db),
        Authorize: AuthJWT = Depends()
    ):
    Authorize.jwt_required()
    db_recipe = db.query(Recipe).get(recipe_id)
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    for field, value in recipe.dict(exclude_unset=True).items():
        setattr(db_recipe, field, value)
    db.commit()
    return {"message": "Recipe updated successfully"}

@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    recipe = db.query(Recipe).get(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db.delete(recipe)
    db.commit()
    return {"message": "Recipe deleted successfully"}
