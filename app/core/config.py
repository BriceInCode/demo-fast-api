import os
from dotenv import load_dotenv

print(f"DEBUG - Chemin actuel : {os.getcwd()}")  # Afficher le répertoire actuel

# Charger le fichier .env
# load_dotenv()
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")

# Débogage : Vérifie si les variables sont bien chargées
print(f"DEBUG - DATABASE_URL: {os.getenv('DATABASE_URL')}")

settings = Settings()
