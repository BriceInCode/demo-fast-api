from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import User, Livre
from app.schemas import UserCreate, LivreCreate
from jose import jwt
from passlib.context import CryptContext
import secrets

# Configuration JWT
SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 🔹 Format de réponse standardisé
def response(code: int, message: str, data=None):
    return {"code": code, "message": message, "data": data}

# ✅ Service User
class UserService:
    @staticmethod
    def create_user(db: Session, user: UserCreate):
        if db.query(User).filter(User.email == user.email).first():
            return response(400, "L'utilisateur existe déjà.")

        db_user = User(
            name=user.name,
            email=user.email,
            password=pwd_context.hash(user.password),
            created_at=datetime.utcnow(),
            is_active=False
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return response(201, "Utilisateur créé avec succès.", db_user)

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return response(404, "Utilisateur non trouvé.")

        if not user.is_active:
            return response(403, "Compte inactif. Contactez un administrateur.")

        if not pwd_context.verify(password, user.password):
            return response(401, "Mot de passe incorrect.")

        token = create_access_token({"sub": user.email})
        return response(200, "Authentification réussie.", {"user": user, "token": token})

    @staticmethod
    def get_user(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        return response(200, "Utilisateur trouvé.", user) if user else response(404, "Utilisateur non trouvé.")
    
    @staticmethod
    def get_user_by_email(db: Session, email: str):
        user = db.query(User).filter(User.email == email).first()
        return response(200, "Utilisateur trouvé.", user) if user else response(404, "Utilisateur non trouvé.")


    @staticmethod
    def list_users(db: Session):
        users = db.query(User).all()
        return response(200, "Liste des utilisateurs.", users)

    @staticmethod
    def update_user(db: Session, user_id: int, name: str = None, email: str = None):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return response(404, "Utilisateur non trouvé.")

        if name:
            user.name = name
        if email:
            user.email = email

        db.commit()
        return response(200, "Utilisateur mis à jour.", user)

    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return response(404, "Utilisateur non trouvé.")

        db.delete(user)
        db.commit()
        return response(200, "Utilisateur supprimé.")

    @staticmethod
    def reset_password(db: Session, email: str, new_password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return response(404, "Utilisateur non trouvé.")

        user.password = pwd_context.hash(new_password)
        db.commit()
        return response(200, "Mot de passe réinitialisé avec succès.")

    @staticmethod
    def activate_user(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return response(404, "Utilisateur non trouvé.")

        user.is_active = True
        db.commit()
        return response(200, "Utilisateur activé avec succès.")

    @staticmethod
    def deactivate_user(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return response(404, "Utilisateur non trouvé.")

        user.is_active = False
        db.commit()
        return response(200, "Utilisateur désactivé avec succès.")

# ✅ Service Livre
class LivreService:
    @staticmethod
    def create_livre(db: Session, livre: LivreCreate):
        db_livre = Livre(
            titre=livre.titre,
            description=livre.description,
            is_lu=livre.is_lu,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_livre)
        db.commit()
        db.refresh(db_livre)
        return response(201, "Livre créé avec succès.", db_livre)

    @staticmethod
    def get_livre(db: Session, livre_id: int):
        livre = db.query(Livre).filter(Livre.id == livre_id).first()
        return response(200, "Livre trouvé.", livre) if livre else response(404, "Livre non trouvé.")

    @staticmethod
    def list_livres(db: Session):
        livres = db.query(Livre).all()
        return response(200, "Liste des livres.", livres)

    @staticmethod
    def update_livre(db: Session, livre_id: int, titre: str = None, description: str = None, is_lu: bool = None):
        livre = db.query(Livre).filter(Livre.id == livre_id).first()
        if not livre:
            return response(404, "Livre non trouvé.")

        if titre:
            livre.titre = titre
        if description:
            livre.description = description
        if is_lu is not None:
            livre.is_lu = is_lu
        livre.updated_at = datetime.utcnow()

        db.commit()
        return response(200, "Livre mis à jour.", livre)

    @staticmethod
    def delete_livre(db: Session, livre_id: int):
        livre = db.query(Livre).filter(Livre.id == livre_id).first()
        if not livre:
            return response(404, "Livre non trouvé.")

        db.delete(livre)
        db.commit()
        return response(200, "Livre supprimé.")

    @staticmethod
    def emprunter_livre(db: Session, livre_id: int, user_id: int):
        livre = db.query(Livre).filter(Livre.id == livre_id, Livre.user_id == None).first()
        if not livre:
            return response(400, "Ce livre est déjà emprunté ou n'existe pas.")

        livre.user_id = user_id
        livre.emprunte_le = datetime.utcnow()
        db.commit()
        return response(200, "Livre emprunté avec succès.", livre)

    @staticmethod
    def rendre_livre(db: Session, livre_id: int):
        livre = db.query(Livre).filter(Livre.id == livre_id, Livre.user_id != None).first()
        if not livre:
            return response(400, "Ce livre n'est pas emprunté.")

        livre.user_id = None
        livre.emprunte_le = None
        db.commit()
        return response(200, "Livre rendu avec succès.", livre)

# ✅ Statistiques
class StatsService:
    @staticmethod
    def get_stats(db: Session):
        total_users = db.query(User).count()
        total_books = db.query(Livre).count()
        books_borrowed = db.query(Livre).filter(Livre.user_id.isnot(None)).count()
        
        return response(200, "Statistiques récupérées avec succès.", {
            "total_users": total_users,
            "total_books": total_books,
            "books_borrowed": books_borrowed,
            "borrow_rate": round((books_borrowed / total_books) * 100, 2) if total_books > 0 else 0
        })
