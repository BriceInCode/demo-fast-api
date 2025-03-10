from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db
from app.models import User, Livre
from app.schemas import UserCreate, UserResponse, LivreCreate, LivreResponse
from app.services import UserService, LivreService, create_access_token

# Initialisation de FastAPI
app = FastAPI(title="Gestion Utilisateurs & Livres API", version="1.0")

# Configuration OAuth2 pour la protection des routes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Création des routeurs
router = APIRouter()

# ✅ Middleware de protection
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Récupérer l'utilisateur actuel à partir du token."""
    user = UserService.get_user_from_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide ou expiré")
    return user

# ====== ROUTES AUTHENTIFICATION ====== #
@router.post("/login", tags=["Authentification"])
def login(email: str, password: str, db: Session = Depends(get_db)):
    """Authentifier un utilisateur et retourner un token JWT."""
    result = UserService.authenticate_user(db, email, password)
    if result["code"] != 200:
        raise HTTPException(status_code=result["code"], detail=result["message"])
    return result

# ====== ROUTES UTILISATEURS ====== #
@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Utilisateurs"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Créer un nouvel utilisateur sans vérifier si l'email existe déjà."""
    return UserService.create_user(db, user)

@router.put("/users/{user_id}/activate", tags=["Utilisateurs"])
def activate_user(user_id: int, db: Session = Depends(get_db)):
    """Activer un utilisateur."""
    result = UserService.activate_user(db, user_id)
    if result["code"] != 200:
        raise HTTPException(status_code=result["code"], detail=result["message"])
    return result

# 🔒 ROUTES PROTÉGÉES (requièrent un token)
@router.get("/users", response_model=List[UserResponse], dependencies=[Depends(get_current_user)], tags=["Utilisateurs"])
def list_users(db: Session = Depends(get_db)):
    """Récupérer la liste des utilisateurs (protégé)."""
    return UserService.list_users(db)

@router.get("/users/{user_id}", response_model=UserResponse, dependencies=[Depends(get_current_user)], tags=["Utilisateurs"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Récupérer un utilisateur par son ID (protégé)."""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé.")
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)], tags=["Utilisateurs"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Supprimer un utilisateur (protégé)."""
    user = UserService.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé.")

# ====== ROUTES LIVRES ====== #
@router.post("/livres", response_model=LivreResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)], tags=["Livres"])
def create_livre(livre: LivreCreate, db: Session = Depends(get_db)):
    """Créer un nouveau livre (protégé)."""
    return LivreService.create_livre(db, livre)

@router.get("/livres", response_model=List[LivreResponse], dependencies=[Depends(get_current_user)], tags=["Livres"])
def list_livres(db: Session = Depends(get_db)):
    """Récupérer la liste des livres (protégé)."""
    return LivreService.list_livres(db)

@router.get("/livres/{livre_id}", response_model=LivreResponse, dependencies=[Depends(get_current_user)], tags=["Livres"])
def get_livre(livre_id: int, db: Session = Depends(get_db)):
    """Récupérer un livre par son ID (protégé)."""
    livre = LivreService.get_livre_by_id(db, livre_id)
    if not livre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livre non trouvé.")
    return livre

@router.put("/livres/{livre_id}/status", response_model=LivreResponse, dependencies=[Depends(get_current_user)], tags=["Livres"])
def update_livre_status(livre_id: int, is_lu: bool, db: Session = Depends(get_db)):
    """Mettre à jour le statut d'un livre (protégé)."""
    livre = LivreService.update_livre_status(db, livre_id, is_lu)
    if not livre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livre non trouvé.")
    return livre

@router.delete("/livres/{livre_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)], tags=["Livres"])
def delete_livre(livre_id: int, db: Session = Depends(get_db)):
    """Supprimer un livre (protégé)."""
    livre = LivreService.delete_livre(db, livre_id)
    if not livre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livre non trouvé.")

# Ajout du routeur à l'application
app.include_router(router)

# Route racine
@app.get("/", tags=["Général"])
def root():
    return {"message": "Bienvenue sur l'API de gestion des utilisateurs et des livres"}
