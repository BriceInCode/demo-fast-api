from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # ✅ Correction (VARCHAR(100))
    email = Column(String(255), unique=True, index=True, nullable=False)  # ✅ Correction
    password = Column(String(255), nullable=False)  # ✅ Correction
    is_active = Column(Boolean, default=True)  
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relation avec Livre (Un utilisateur peut avoir plusieurs livres)
    livres = relationship("Livre", back_populates="user", cascade="all, delete-orphan")

class Livre(Base):
    __tablename__ = "livres"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), index=True, nullable=False)  # ✅ Correction
    description = Column(String(500), nullable=True)  # ✅ Correction (limite optionnelle)
    is_lu = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    emprunte_le = Column(DateTime, nullable=True)

    # Clé étrangère vers User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # ✅ Correction (plus `unique=True`)

    # Relation avec User
    user = relationship("User", back_populates="livres")
