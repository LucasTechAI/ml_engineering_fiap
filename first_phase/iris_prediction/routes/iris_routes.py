from .schemas import IrisInput, IrisPredictionOut, ClassesResponse, PredictionLogOut
from fastapi import APIRouter, Depends, Query
from .deps import get_current_user, get_db
from database.models import PredictionLog
from sqlalchemy.orm import Session
import numpy as np
import joblib
import os

router = APIRouter()

MODEL_PATH = os.path.join("model", "random_forest_iris.pkl")
model = joblib.load(MODEL_PATH)
target_names = ["setosa", "versicolor", "virginica"]

@router.post("/predict", response_model=IrisPredictionOut)
def predict_iris(data: IrisInput, current_user=Depends(get_current_user), db=Depends(get_db)):
    features = np.array([[data.sepal_length, data.sepal_width, data.petal_length, data.petal_width]])
    prediction = model.predict(features)
    predicted_class = target_names[prediction[0]]

    new_log = PredictionLog(
        sepal_length=data.sepal_length,
        sepal_width=data.sepal_width,
        petal_length=data.petal_length,
        petal_width=data.petal_width,
        predicted_class=predicted_class
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return {"prediction": int(prediction[0]), "class_name": predicted_class}

@router.get("/classes", response_model=ClassesResponse)
def get_classes():
    return {"classes": target_names}


@router.get("/predictions", response_model=list[PredictionLogOut])
def get_predictions(
    limit: int = Query(5, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    predictions = db.query(PredictionLog).offset(offset).limit(limit).all()
    return predictions