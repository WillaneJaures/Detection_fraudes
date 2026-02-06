import streamlit as st
import requests
import pandas as pd
import numpy as np
import json

# Configuration de la page
st.set_page_config(
    page_title="Détection de Fraude Carte de Crédit",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Style CSS
st.markdown("""
    <style>
    .big-title {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1E3A8A;
    }
    .result-box {
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin: 2rem 0;
        font-size: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .fraud-yes {
        background-color: #ef4444;
        color: white;
        border-left: 5px solid #dc2626;
    }
    .fraud-no {
        background-color: #10b981;
        color: white;
        border-left: 5px solid #059669;
    }
    .warning-box {
        background-color: #fef3c7;
        color: #92400e;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #f59e0b;
        margin: 1rem 0;
    }
    .section-title {
        background-color: #f8fafc;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 1.5rem 0 1rem 0;
        color: #1e40af;
        font-weight: bold;
    }
    /* Masquer complètement la sidebar */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Titre
st.markdown('<div class="big-title">💳 Détection de Fraude Bancaire</div>', unsafe_allow_html=True)

# URL de l'API (à adapter selon votre configuration)
API_URL = "http://127.0.0.1:8000"

# Interface principale
st.markdown('<div class="warning-box">⚠️ Pour des raisons de sécurité, les informations sensibles (numéro de carte, nom) ne sont pas collectées.</div>', unsafe_allow_html=True)

# Formulaire d'entrée manuelle
st.markdown('<div class="section-title">📊 Informations de la Transaction</div>', unsafe_allow_html=True)

# Grille en 2 colonnes
col1, col2 = st.columns(2)

with col1:
    st.subheader("Montant & Temps")
    amount = st.number_input("Montant (€)", min_value=0.01, max_value=100000.0, value=100.0, step=0.01)
    time = st.number_input("Temps (secondes depuis début)", min_value=0, max_value=259200, value=50000, step=1)
    
    st.subheader("Caractéristiques Principales V1-V10")
    v1 = st.number_input("V1", value=-1.3, format="%.4f", help="Première composante principale")
    v2 = st.number_input("V2", value=0.5, format="%.4f", help="Deuxième composante principale")
    v3 = st.number_input("V3", value=-0.8, format="%.4f", help="Troisième composante principale")
    v4 = st.number_input("V4", value=1.2, format="%.4f", help="Quatrième composante principale")
    v5 = st.number_input("V5", value=-0.3, format="%.4f", help="Cinquième composante principale")

with col2:
    st.subheader("Caractéristiques V11-V20")
    v11 = st.number_input("V11", value=0.8, format="%.4f", help="Onzième composante principale")
    v12 = st.number_input("V12", value=-0.4, format="%.4f", help="Douzième composante principale")
    v13 = st.number_input("V13", value=0.2, format="%.4f", help="Treizième composante principale")
    v14 = st.number_input("V14", value=-0.3, format="%.4f", help="Quatorzième composante principale")
    v15 = st.number_input("V15", value=0.1, format="%.4f", help="Quinzième composante principale")
    v16 = st.number_input("V16", value=-0.1, format="%.4f", help="Seizième composante principale")
    v17 = st.number_input("V17", value=-0.2, format="%.4f", help="Dix-septième composante principale")
    v18 = st.number_input("V18", value=0.0, format="%.4f", help="Dix-huitième composante principale")
    v19 = st.number_input("V19", value=0.1, format="%.4f", help="Dix-neuvième composante principale")
    v20 = st.number_input("V20", value=-0.1, format="%.4f", help="Vingtième composante principale")

# Bouton de prédiction
st.markdown("---")
predict_button = st.button("🔍 Analyser la Transaction", type="primary", use_container_width=True)

if predict_button:
    # Préparer les données pour l'API
    transaction_data = {
        "Time": float(time),
        "V1": v1, "V2": v2, "V3": v3, "V4": v4, "V5": v5,
        "V6": -0.5, "V7": 0.2, "V8": -0.1, "V9": 0.3, "V10": -0.2,
        "V11": v11, "V12": v12, "V13": v13, "V14": v14, "V15": v15,
        "V16": v16, "V17": v17, "V18": v18, "V19": v19, "V20": v20,
        "V21": 0.0, "V22": 0.0, "V23": 0.0, "V24": 0.0, "V25": 0.0,
        "V26": 0.0, "V27": 0.0, "V28": 0.0,
        "Amount": float(amount)
    }
    
    # Appel API
    try:
        with st.spinner("🔐 Analyse de sécurité en cours..."):
            response = requests.post(f"{API_URL}/predict", 
                                    json=transaction_data, 
                                    timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            is_fraud = result.get("is_fraud")
            probability = result.get("fraud_probability", 0.0)
            
            # Afficher le résultat
            st.markdown("---")
            st.markdown("### 📊 Résultat de l'Analyse")
            
            if is_fraud:
                st.markdown(
                    '<div class="result-box fraud-yes">'
                    '🚨 <strong>FRAUDE DÉTECTÉE</strong><br>'
                    f'Score de risque: {probability:.1%}'
                    '</div>',
                    unsafe_allow_html=True
                )
                
                st.error("**Actions Immédiates Recommandées :**")
                st.write("1. 🔒 Bloquer la transaction immédiatement")
                st.write("2. 📞 Contacter le titulaire de la carte")
                st.write("3. ⚠️ Marquer le compte pour surveillance renforcée")
                st.write("4. 📋 Conserver les logs pour investigation")
                
            else:
                st.markdown(
                    '<div class="result-box fraud-no">'
                    '✅ <strong>TRANSACTION VALIDE</strong><br>'
                    f'Niveau de confiance: {(1-probability):.1%}'
                    '</div>',
                    unsafe_allow_html=True
                )
                
                st.success("**Statut : Transaction autorisée**")
                st.balloons()
                
        else:
            error_msg = response.json().get("detail", "Erreur de serveur")
            st.error(f"❌ Erreur API: {error_msg}")
            
    except requests.exceptions.ConnectionError:
        st.error("🔌 Impossible de se connecter à l'API de détection")
        st.info("""
        **Pour démarrer l'API :**
        ```bash
        uvicorn fraud_api:app --reload --port 8000
        ```
        
        **Ou si votre fichier s'appelle différemment :**
        ```bash
        uvicorn main:app --reload --port 8000
        ```
        """)
    except Exception as e:
        st.error(f"⚠️ Erreur inattendue: {str(e)}")

# Section informations
with st.expander("ℹ️ À propos de ce système"):
    st.markdown("""
    ### Système de Détection de Fraude
    
    **Fonctionnement :**
    - Analyse en temps réel des transactions bancaires
    - Détection d'anomalies par algorithme de Machine Learning
    - Évaluation basée sur 30 caractéristiques (V1-V28, Temps, Montant)
    
    **Caractéristiques analysées :**
    - **Temps** : Heure de la transaction
    - **Montant** : Valeur de la transaction
    - **V1-V28** : Composantes principales issues du PCA (anonymisées)
    
    **Algorithme utilisé :**
    - Entraîné sur le dataset Kaggle Credit Card Fraud Detection
    - Taux de détection optimisé pour minimiser les faux positifs
    
    *Note : Toutes les données sont anonymisées pour protéger la vie privée.*
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 1rem;'>
    <small>💳 Système de Détection de Fraude - Machine Learning<br>
    Sécurité Bancaire & Prévention des Risques</small>
    </div>
    """,
    unsafe_allow_html=True
)