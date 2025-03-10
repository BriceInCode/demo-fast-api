from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

# 📚 Modèle de base pour un livre
class LivreBase(BaseModel):
    titre: str = Field(..., min_length=3, max_length=255, example="Le Petit Prince")
    description: Optional[str] = Field(None, max_length=500, example="Un conte philosophique.")
    is_lu: bool = Field(False, example=True)

# 📚 Modèle pour la création d'un livre
class LivreCreate(LivreBase):
    pass

# 📚 Modèle pour la réponse d'un livre
class LivreResponse(LivreBase):
    id: int
    emprunte_le: Optional[datetime] = None
    user_id: Optional[int] = None

    class Config:
        from_attributes = True  # ✅ Convertit les objets SQLAlchemy en dict Pydantic

# 👤 Modèle de base pour un utilisateur
class UserBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, example="Jean Dupont")
    email: EmailStr = Field(..., example="jean.dupont@example.com")  # ✅ Email validé

# 👤 Modèle pour la création d'un utilisateur
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, example="password123")

# 👤 Modèle pour la réponse utilisateur
class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool = Field(True, example=True)  # ✅ Assure que l'utilisateur est actif

    class Config:
        from_attributes = True  # ✅ Convertit les objets SQLAlchemy en dict Pydantic
