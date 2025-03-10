from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.items import router  
from app.database import init_db  # ✅ Import de la fonction init_db

app = FastAPI(
    title="Bibliothèque API",
    description="Une API pour gérer les utilisateurs et les livres",
    version="1.0",
    contact={"name": "Support API", "email": "support@example.com"},
)

# ✅ Initialiser la base de données au démarrage
@app.on_event("startup")
def startup():
    init_db()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ajouter les routes (Un seul router)
app.include_router(router)

@app.get("/", tags=["Root"])
def root():
    return {"message": "Bienvenue sur l'API de gestion des utilisateurs et des livres"}
