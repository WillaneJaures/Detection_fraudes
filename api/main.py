from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal
import joblib
import json
import pandas
import uvicorn
import numpy as np
import os


app = FastAPI(title="Credit Card Fraud Detection")


#chargement des artefects au demarrage-------------------


MODEL_DIR = '../models'
model = None
metrics = None
FEATURE_LIST = None


try:
    model = joblib.load(os.path.join(MODEL_DIR, 'logr_model.pkl'))
    print("Modele charge avec succes")
except Exception as e:
    print(f" Erreur lors du chargement du modele: {e}")

try:
    with open(os.path.join(MODEL_DIR, 'metrics.json'), 'r', encoding='utf-8') as f :
        metrics = json.load(f)
    print("Metrics chargees avec succes")
except UnicodeDecodeError:
    print(f"❌ metrics.json n'est pas au format UTF-8")
    print("   Utilisez json.dump() au lieu de joblib.dump()")
    metrics = None
except Exception as e:
    print(f"❌ Erreur lors du chargement des métriques: {e}")
    metrics = None

try:
    with open(os.path.join(MODEL_DIR, 'feature_list.json'), 'r') as f:
        FEATURE_LIST = json.load(f)
    print("✅ Feature list chargée avec succès")
except Exception as e:
    print(f"⚠️  Fichier feature_list.json non trouvé (optionnel): {e}")


class TransactionInput(BaseModel):
    # Time est souvent en secondes dans ce dataset
    Time: float = Field(..., description="Temps écoulé en secondes depuis la 1ère transaction")
    
    # Les composantes PCA (V1 à V28)
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    
    # Le montant de la transaction
    Amount: float = Field(..., gt=0, description="Montant de la transaction")

    # Exemple pour la documentation de l'API (Swagger UI)
    class Config:
        schema_extra = {
            "example": {
                "Time": 0.0,
                "V1": -1.359807,
                "V2": -0.072781,
                "V3": 2.536347,
                "V4": 1.378155,
                "V5": -0.338321,
                "V6": 0.462388,
                "V7": 0.239599,
                "V8": 0.098698,
                "V9": 0.363787,
                "V10": 0.090794,
                "V11": -0.551600,
                "V12": -0.617801,
                "V13": -0.991390,
                "V14": -0.311169,
                "V15": 1.468177,
                "V16": -0.470401,
                "V17": 0.207971,
                "V18": 0.025791,
                "V19": 0.403993,
                "V20": 0.251412,
                "V21": -0.018307,
                "V22": 0.277838,
                "V23": -0.110474,
                "V24": 0.066928,
                "V25": 0.128539,
                "V26": -0.189115,
                "V27": 0.133558,
                "V28": -0.021053,
                "Amount": 149.62
            }
        }

@app.get("/health")
def health():
    """Vérification de la santé de l'API et du modèle"""
    try:
        model_ok = model is not None 
        metrics_ok = metrics is not None

        all_ok = model_ok and metrics_ok

        status_details = {
            "status": "healthy" if all_ok else "unhealthy",
            "model_loaded" : model_ok,
            "metrics_loaded": metrics_ok

        }

        status_details["message"] = (
            "API et tous les composants operationnels" if all_ok
            else "Certains composants ne sont pas charges"
        )

        return status_details
    except Exception as e:
        return {
            
            "status": "error",
            "message": f"Erreur de sante: {str(e)}"
            
        }

@app.get("/metrics")
def get_metrics():
    """
    Endpoint pour récupérer les métriques du modèle
    """
    if metrics is None:
        raise HTTPException(
            status_code=404,
            detail="Les métriques ne sont pas disponibles. Régénérez metrics.json avec json.dump()."
        )
    
    return {
        "metrics": metrics,
        "message": "Métriques chargées depuis models/metrics.json"
    }

@app.post("/predict")
def predict(transaction: TransactionInput):
    """
    Docstring for predict
    
    :param transaction: Description
    :type transaction: TransactionInput
    Prediction de fraude pour une transaction donnee
    """

    #Verifions le model est charge
    if model is None:
        raise HTTPException(status_code=503, details="Modele non charge")
    
    try:
        #Convertir les donees recues en dictionnaire
        data_dict = transaction.dict()

        #.convertir en DataFrame pour garantir l'ordre des colonnes
        input_df = pandas.DataFrame([data_dict])

        #pour etre sur que l'ordre des colonne correspond
        if FEATURE_LIST:
            input_df = input_df[FEATURE_LIST]
        
        prediction = model.predict(input_df)[0]

        probability = model.predict_proba(input_df)[0][1]

        #formater la reponse
        result = {
            "prediction": int(prediction),
            "is_fraud": bool(prediction == 1),
            "fraud_probability": float(probability),
            "risk_level" : "high" if probability > 0.8 else "low"

        }

        return result
    
    except Exception as e:
        raise HTTPException(status_code=400, detail = f"Erreur lors de la prediction: {str(e)}")