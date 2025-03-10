from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# ✅ Connexion à la base de données MySQL (remplacement du driver si nécessaire)
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace("mysql://", "mysql+pymysql://")

# ✅ Création de l'engine SQLAlchemy
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
    print("✅ Connexion à la base de données réussie.")
except Exception as e:
    print(f"❌ Erreur de connexion à la base de données : {e}")

# ✅ Création d'une session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Base pour les modèles SQLAlchemy
Base = declarative_base()

# ✅ Fonction pour récupérer la session de la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Initialisation de la base de données (création automatique des tables)
def init_db():
    try:
        print("🔄 Vérification et création des tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables créées avec succès (si elles n'existaient pas).")
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables : {e}")
