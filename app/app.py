from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from .constantes import *
from flask_login import LoginManager

# récupération du chemin absolu du dossier de l'application
chemin_actuel = os.path.dirname(os.path.abspath(__file__))

templates = os.path.join(chemin_actuel, 'templates')
statics = os.path.join(chemin_actuel, 'statics')

# information à Flask que les templates se trouvent dans le dossier templates, idem pour les statics
app = Flask("Minimusée", template_folder=templates, static_folder=statics)

# instanciation de la db

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATION
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)
login_manager = LoginManager(app)
from app.routes import generic

# fonction qui récupère les modèles de la base, si le modèle ne correspond pas à la db il créé la table
# si elle existe, vérification des champs
def init_app():
    db.create_all()