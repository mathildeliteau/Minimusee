# définition du modèle de données
from ..app import db
from sqlalchemy import and_

# la classe Artiste hérite de la classe modèle de la db
class Artiste(db.Model):
    # nom de la table telle qu'elle existe dans la base
    __tablename__ = 'Artiste'
    # Création du modèle
    artiste_id = db.Column(db.Integer, unique=True, nullable=False, autoincrement=True, primary_key=True)
    artiste_nom = db.Column(db.Text, nullable=False)
    date_naissance = db.Column(db.Integer)
    date_mort = db.Column(db.Integer)
    artiste_activite = db.Column(db.Text)

    @staticmethod
    def insertion_artiste(nom, date_naissance, date_mort, activite):
        """ Permet l'insertion d'un nouvel artiste en base
        :param nom: nom de l'artiste
        :param date_naissance: date de naissance de l'artiste
        :param date_mort: date de mort de l'artiste
        :param activite: activité de l'artiste
        :type nom: str
        :type date_naissance: int
        :type date_mort: int
        :type activite: str
        :return: nouvelle entrée en base
        :rtype: tuple
        """
        # création d'une liste vide pour y stocker les éventuelles erreurs
        erreurs = []
        if not nom:
            erreurs.append("Le nom fourni est vide")
        if not date_naissance:
            erreurs.append("La date de naissance fournie est vide")
        if not date_mort:
            erreurs.append("La date de décès fournie est vide")
        if not activite:
            erreurs.append("L'activité fournie est vide")

        # On vérifie que personne n'a entré cet artiste
        uniques = Artiste.query.filter(
            Artiste.artiste_nom == nom
        ).count()
        if uniques > 0:
            erreurs.append("Le nom est déjà inscrit dans notre base de données")

        # Si on a au moins une erreur
        if len(erreurs) > 0:
            return False, erreurs

        # On crée une variable stockant les informations des champs
        artiste = Artiste(
            artiste_nom=nom,
            date_naissance=date_naissance,
            date_mort=date_mort,
            artiste_activite=activite
        )

        try:
            # On l'ajoute au transport vers la base de données
            db.session.add(artiste)
            # On envoie le paquet
            db.session.commit()

            # On renvoie l'artiste
            return True, artiste
        except Exception as erreur:
            # si le résultat du try retourne une erreur, la session de la base de données reste ouverte
            # et bloque la session d'insertion: si l'insertion ou le commit a une erreur, la session
            # reste ouverte et empêche de faire des insertions voire la lecture
            db.session.rollback()
            return False, [str(erreur)]

    @staticmethod
    def modification_artiste(nom, date_naissance, date_mort, activite, ids_oeuvres, id_artiste):
        """ Permet la modification d'une entrée de la table Artiste
            :param nom: nom de l'artiste
            :param date_naissance: date de naissance de l'artiste
            :param date_mort: date de mort de l'artiste
            :param activite: activité de l'artiste
            :param ids_oeuvres: liste des id des oeuvres
            :param id_artiste: id de l'artiste
            :type nom: str
            :type date_naissance: int
            :type date_mort: int
            :type activite: str
            :type ids_oeuvres: list
            :type id_artiste: int
            :return: entrée modifiée en base
            :rtype: tuple
            """
        # on caste ids_oeuvres pour avoir des integer
        ids_oeuvres = [int(id_oeuvre) for id_oeuvre in ids_oeuvres]
        # Création d'une liste vide qui stocke les éventuelles erreurs
        erreurs = []
        if not nom:
            erreurs.append("Le nom fourni est vide")
        if not date_naissance:
            erreurs.append("La date de naissance fournie est vide")
        if not date_mort:
            erreurs.append("La date de décès fournie est vide")
        if not activite:
            erreurs.append("L'activité fournie est vide")
        if not id_artiste:
            erreurs.append("L'id de l'artiste fourni est vide")


        # On vérifie que cet artiste est en base
        current_artiste = Artiste.query.filter(
            Artiste.artiste_id == id_artiste
        )
        if current_artiste.count() == 0:
            erreurs.append("L'id est absent de notre base de données")

        # Si on a au moins une erreur
        if len(erreurs) > 0:
            return False, erreurs
        # récupération du premier résultat de la requête current_artiste
        # (pour voir la requête SQL faire un print(current_artiste)
        artiste = current_artiste.first()
        if nom:
            artiste.artiste_nom = nom
        if date_naissance:
            artiste.date_naissance = int(date_naissance)
        if date_mort:
            artiste.date_mort = int(date_mort)
        if activite:
            artiste.artiste_activite = activite

        try:
            # On l'ajoute au transport vers la base de données
            db.session.add(artiste)
            # liste des id oeuvre des oeuvres en base
            oeuvres_base = [oeuvre_base.oeuvre_id for oeuvre_base in
                             Oeuvre_artiste.query.filter(Oeuvre_artiste.artiste_id == id_artiste).all()]
            for id_oeuvre in ids_oeuvres:
                # si l'id de l'oeuvre est en base, alors on ne fait rien
                if id_oeuvre not in oeuvres_base:
                    # si l'oeuvre n'est pas encore associée à l'artiste
                    db.session.add(Oeuvre_artiste(oeuvre_id=id_oeuvre, artiste_id=id_artiste))
            for oeuvre_base in oeuvres_base:
                # si l'oeuvre en base n'est pas présente dans la requête de l'utilisateur, on le supprime
                if oeuvre_base not in ids_oeuvres:
                    db.session.delete(Oeuvre_artiste.query.filter(
                        and_(Oeuvre_artiste.oeuvre_id == oeuvre_base, Oeuvre_artiste.artiste_id == id_artiste)).first())

            db.session.commit()
            return True, None

        except Exception as erreur:
            # si le résultat du try retourne une erreur, la session de la base de données reste ouverte
            # et bloque la session d'insertion: si l'insertion ou le commit a une erreur alors la session
            # reste ouverte et empêche de faire des insertions voire la lecture
            db.session.rollback()
            return False, [str(erreur)]

    @staticmethod
    def suppression_artiste(id_artiste):
        """ Permet la suppression d'une entrée de la table Artiste
            :param nom: nom de l'artiste
            :param date_naissance: date de naissance de l'artiste
            :param date_mort: date de mort de l'artiste
            :param activite: activité de l'artiste
            :type param: str
            :type date_naissance: int
            :type date_mort: int
            :type activite: str
            :return: entrée supprimée en base
            :rtype: tuple
            """
        # Création d'une liste vide pour stcker les éventuelles erreurs
        erreurs = []
        if not id_artiste:
            erreurs.append("L'id fourni est vide")

        # On vérifie que l'artiste est bien en base
        current_artiste = Artiste.query.filter(
            Artiste.artiste_id == id_artiste
        )
        if current_artiste.count() == 0:
            erreurs.append("L'artiste n'est pas inscrit dans notre base de données")

        # Si on a au moins une erreur
        if len(erreurs) > 0:
            return False, erreurs

        try:
            # on supprime les relations de l'artiste avec les oeuvres
            for oeuvre in (Oeuvre_artiste.query.filter(Oeuvre_artiste.artiste_id == id_artiste).all()):
                db.session.delete(oeuvre)
            # On l'ajoute au transport vers la base de données
            db.session.delete(current_artiste.first())
            db.session.commit()
            return True, None

        except Exception as erreur:
            # si le résultat du try retourne une erreur, la session de la base de données reste ouverte
            # et bloque la session d'insertion: si l'insertion ou le commit a une erreur alors la session
            # reste ouverte et empêche de faire des insertions voire la lecture
            db.session.rollback()
            return False, [str(erreur)]

# la classe Lieu hérite de la classe modèle de la db
class Lieu(db.Model):
    # nom de la table telle qu'elle existe dans la base
    __tablename__ = 'Lieu'
    # Création du modèle
    lieu_id = db.Column(db.Integer, unique=True, nullable=False, autoincrement=True, primary_key=True)
    lieu_nom = db.Column(db.Text, nullable=False)
    lieu_ville = db.Column(db.Text)
    lieu_pays = db.Column(db.Text)

    oeuvres = db.relationship("Oeuvre", backref="lieu", lazy="dynamic")

    @staticmethod
    def insertion_lieu(nom, ville, pays):
        """ Permet l'insertion d'un nouveau lieu en base
            :param nom: nom du lieu
            :param ville: nom de la ville du lieu
            :param pays: nom du pays du lieu
            :type nom: str
            :type ville: str
            :type pays: str
            :return: nouvelle entrée en base
            :rtype: tuple
        """
        # création d'une liste vide pour y stocker les éventuelles erreurs
        erreurs = []
        if not nom:
            erreurs.append("Le nom fourni est vide")
        if not ville:
            erreurs.append("La ville fournie est vide")
        if not pays:
            erreurs.append("Le pays fourni est vide")


        # On vérifie que personne n'a enregistré ce lieu
        uniques = Lieu.query.filter(
            Lieu.lieu_nom == nom
        ).count()
        if uniques > 0:
            erreurs.append("Le nom est déjà inscrit dans notre base de données")

        # Si on a au moins une erreur
        if len(erreurs) > 0:
            return False, erreurs

        # On crée un utilisateur
        lieu = Lieu(
            lieu_nom=nom,
            lieu_ville=ville,
            lieu_pays=pays
        )

        try:
            # On l'ajoute au transport vers la base de données
            db.session.add(lieu)
            # On envoie le paquet
            db.session.commit()

            # On renvoie le lieu
            return True, lieu
        except Exception as erreur:
            # si le résultat du try retourne une erreur, la session de la base de données reste ouverte
            # et bloque la session d'insertion: si l'insertion ou le commit a une erreur donc la session
            # reste ouverte et empêche de faire des insertions voire la lecture
            db.session.rollback()
            return False, [str(erreur)]

    @staticmethod
    def modification_lieu(nom, ville, pays, id_lieu):
        """ Permet la modification d'une entrée de la table Lieu
            :param nom: nom du lieu
            :param ville: nom de la ville du lieu
            :param pays: nom du pays du lieu
            :type nom: str
            :type ville: str
            :type pays: str
            :type id_lieu: int
            :return: entrée modifiée en base
            :rtype: tuple
            """
        erreurs = []
        if not nom:
            erreurs.append("Le nom fourni est vide")
        if not ville:
            erreurs.append("La ville de création fournie est vide")
        if not pays:
            erreurs.append("Le pays fourni est vide")
        if not id_lieu:
            erreurs.append("L'id du lieu fourni est vide")

        # On vérifie que personne n'a utilisé ce lieu
        current_lieu = Lieu.query.filter(
            Lieu.lieu_id == id_lieu
        )
        if current_lieu.count() == 0:
            erreurs.append("L'id est absent de notre base de données")

        # Si on a au moins une erreur
        if len(erreurs) > 0:
            return False, erreurs
        # récupération du premier résultat de la requête current_lieu (pour voir la requête SQL faire un print(current_lieu)
        lieu = current_lieu.first()
        if nom:
            lieu.lieu_nom = nom
        if ville:
            lieu.lieu_ville = ville
        if pays:
            lieu.lieu_pays = pays

        try:
            # On l'ajoute au transport vers la base de données
            db.session.add(lieu)
            db.session.commit()
            return True, lieu

        except Exception as erreur:
            # si le résultat du try retourne une erreur, la session de la base de données reste ouverte
            # et bloque la session d'insertion: si l'insertion ou le commit a une erreur donc la session
            # reste ouverte et empêche de faire des insertions voire la lecture
            db.session.rollback()
            return False, [str(erreur)]

    @staticmethod
    def supprimer_lieu(id_lieu):
        """ Permet la suppression d'une entrée de la table Lieu
            :param id_lieu: id du lieu
            :type id_lieu: int
            :return: entrée supprimée en base
            :rtype: tuple
            """
        # Création d'une liste vide qui stocke les éventuelles erreurs
        erreurs = []
        if not id_lieu:
            erreurs.append("L'id fourni est vide")

        # On vérifie que le lieu est en base
        current_lieu = Lieu.query.filter(
            Lieu.lieu_id == id_lieu
        )
        if current_lieu.count() == 0:
            erreurs.append("Le lieu n'est pas inscrit dans notre base de données")

        # Si on a au moins une erreur
        if len(erreurs) > 0:
            return False, erreurs

        try:
            # on supprime les relations du lieu avec les oeuvres
            Oeuvre.query.filter_by(lieu_conservation=id_lieu).update(dict(lieu_conservation=None))
            db.session.delete(current_lieu.first())
            db.session.commit()
            return True, None
        except Exception as erreur:
            db.session.rollback()
            return False, [str(erreur)," Vous ne pouvez pas supprimer ce lieu car des oeuvres de notre base y sont conservées"]

        except Exception as erreur:
            # si le résultat du try retourne une erreur, la session de la base de données reste ouverte
            # et bloque la session d'insertion: si l'insertion ou le commit a une erreur donc la session
            # reste ouverte et empêche de faire des insertions voire la lecture
            db.session.rollback()
            return False, [str(erreur)]

# la classe Oeuvre hérite de la classe modèle de la db
class Oeuvre(db.Model):
    # nom de la table telle qu'elle existe dans la base
    __tablename__ = 'Oeuvre'
    # Création du modèle
    oeuvre_id = db.Column(db.Integer, unique=True, nullable=False, autoincrement=True, primary_key=True)
    oeuvre_titre = db.Column(db.Text, nullable=False)
    date_creation = db.Column(db.Integer)
    lieu_conservation = db.Column(db.Integer, db.ForeignKey('Lieu.lieu_id'))

    @staticmethod
    def insertion_oeuvre(titre, creation, id_lieu, ids_artistes):
        """ Permet l'insertion d'une nouvelle oeuvre en base
            :param titre: titre de l'oeuvre
            :param creation: date de creation de l'oeuvre
            :param id_lieu: id du lieu
            :param ids_artistes: liste des id des artistes
            :type titre: str
            :type creation: int
            :type id_lieu: int
            :type ids_artistes: list
            :return: nouvelle entrée en base
            :rtype: tuple
            """
        # création d'une liste vide pour y stocker les éventuelles erreurs
        erreurs = []
        if not titre:
            erreurs.append("Le titre fourni est vide")
        if not creation:
            erreurs.append("La date de création fournie est vide")
        if not id_lieu:
            erreurs.append("Le lieu fourni est vide")

        # On vérifie que cette oeuvre est bien en base
        uniques = Oeuvre.query.filter(
            Oeuvre.oeuvre_titre == titre
        ).count()
        if uniques > 0:
            erreurs.append("Le titre est déjà inscrit dans notre base de données")

        # Si on a au moins une erreur
        if len(erreurs) > 0:
            return False, erreurs

        # On crée une oeuvre
        oeuvre = Oeuvre(
            oeuvre_titre=titre,
            date_creation=creation,
            lieu_conservation=id_lieu
        )

        try:
            # On l'ajoute au transport vers la base de données
            db.session.add(oeuvre)
            db.session.commit()
            oeuvre_id = (Oeuvre.query.filter(Oeuvre.oeuvre_titre == titre).first()).oeuvre_id
            try:
                for id_artiste in ids_artistes:
                    oeuvre_artiste = Oeuvre_artiste(
                        oeuvre_id=int(oeuvre_id),
                        artiste_id=int(id_artiste)
                    )
                    db.session.add(oeuvre_artiste)
                db.session.commit()
                return True, oeuvre_artiste

            except Exception as erreur:
                db.session.rollback()
                return False, [str(erreur)]

        except Exception as erreur:
            # si le résultat du try retourne une erreur, la session de la base de données reste ouverte
            # et bloque la session d'insertion: si l'insertion ou le commit a une erreur donc la session
            # reste ouverte et empêche de faire des insertions voire la lecture
            db.session.rollback()
            return False, [str(erreur)]


    @staticmethod
    def modification_oeuvre(titre, creation, id_lieu, ids_artistes, id_oeuvre):
        """ Permet la modification d'une entrée de la table Oeuvre
            :param titre: titre de l'oeuvre
            :param creation: date de creation de l'oeuvre
            :param id_lieu: id du lieu
            :param ids_artistes: liste des id des artistes
            :param id_oeuvre: id de l'oeuvre
            :type titre: str
            :type creation: int
            :type id_lieu: int
            :type ids_artistes: list
            :type id_oeuvre: int
            :return: entrée modifiée en base
            :rtype: tuple
            """
        # on caste ids_artistes pour avoir des integer
        ids_artistes = [int(id_artiste) for id_artiste in ids_artistes]
        erreurs = []
        if not titre:
            erreurs.append("Le titre fourni est vide")
        if not creation:
            erreurs.append("La date de création fournie est vide")
        if not id_lieu:
            erreurs.append("Le lieu fourni est vide")
        if not id_oeuvre:
            erreurs.append("L'id de l'oeuvre fourni est vide")

        # On vérifie que l'oeuvre est bien en base
        current_oeuvre = Oeuvre.query.filter(
            Oeuvre.oeuvre_id == id_oeuvre
        )
        if current_oeuvre.count() == 0:
            erreurs.append("L'id est absent de notre base de données")

        # Si on a au moins une erreur
        if len(erreurs) > 0:
            return False, erreurs
        # récupération du premier résultat de la requête current_oeuvre
        # (pour voir la requête SQL faire un print(current_oeuvre)
        oeuvre = current_oeuvre.first()
        if titre:
            oeuvre.oeuvre_titre = titre
        if creation:
            oeuvre.date_creation = int(creation)
        if id_lieu:
            oeuvre.lieu_conservation = int(id_lieu)

        try:
            # On l'ajoute au transport vers la base de données
            db.session.add(oeuvre)
            # liste des id artiste des artistes en base
            artistes_base = [artiste_base.artiste_id for artiste_base in
                             Oeuvre_artiste.query.filter(Oeuvre_artiste.oeuvre_id == id_oeuvre).all()]
            for id_artiste in ids_artistes:
                # si l'id de l'artiste est en base, alors on ne fait rien
                if id_artiste not in artistes_base:
                    # si l'artiste n'est pas encore associé à l'oeuvre
                    db.session.add(Oeuvre_artiste(oeuvre_id=id_oeuvre, artiste_id=id_artiste))
            for artiste_base in artistes_base:
                # si l'artiste en base n'est pas présent dans la requête de l'utilisateur, on le supprime
                if artiste_base not in ids_artistes:
                    db.session.delete(Oeuvre_artiste.query.filter(
                        and_(Oeuvre_artiste.artiste_id == artiste_base, Oeuvre_artiste.oeuvre_id == id_oeuvre)).first())

            db.session.commit()
            return True, None

        except Exception as erreur:
            # si le résultat du try retourne une erreur, la session de la base de données reste ouverte
            # et bloque la session d'insertion: si l'insertion ou le commit a une erreur donc la session
            # reste ouverte et empêche de faire des insertions voire la lecture
            db.session.rollback()
            return False, [str(erreur)]

    @staticmethod
    def suppression_oeuvre(id_oeuvre):
        """ Permet la suppression d'une entrée de la table Oeuvre
            :param id_oeuvre: id de l'oeuvre
            :type id_oeuvre: int
            :return: entrée supprimée en base
            :rtype: tuple
            """
        # Création d'une liste vide qui stocke les éventuelles erreurs
        erreurs = []
        if not id_oeuvre:
            erreurs.append("L'id fourni est vide")

        # On vérifie que l'oeuvre est bien en base
        current_oeuvre = Oeuvre.query.filter(
            Oeuvre.oeuvre_id == id_oeuvre
        )
        if current_oeuvre.count() == 0:
            erreurs.append("L'oeuvre n'est pas inscrite dans notre base de données")

        # Si on a au moins une erreur
        if len(erreurs) > 0:
            return False, erreurs

        try:
            # on supprime les relations de l'oeuvre avec les artistes
            for artiste in (Oeuvre_artiste.query.filter(Oeuvre_artiste.oeuvre_id==id_oeuvre).all()):
                db.session.delete(artiste)
            # On l'ajoute au transport vers la base de données
            db.session.delete(current_oeuvre.first())
            db.session.commit()
            return True, None

        except Exception as erreur:
            # si le résultat du try retourne une erreur, la session de la base de données reste ouverte
            # et bloque la session d'insertion: si l'insertion ou le commit a une erreur donc la session
            # reste ouverte et empêche de faire des insertions voire la lecture
            db.session.rollback()
            return False, [str(erreur)]

# la classe Oeuvre_artiste hérite de la classe modèle de la db
class Oeuvre_artiste(db.Model):
    # nom de la table telle qu'elle existe dans la base
    __tablename__ = "Oeuvre_artiste"
    # c'est une table de relation entre Artiste et Oeuvre
    oeuvre_artiste_id = db.Column(db.Integer, unique=True, nullable=False, autoincrement=True, primary_key=True)
    oeuvre_id = db.Column(db.Integer, db.ForeignKey('Oeuvre.oeuvre_id'))
    artiste_id = db.Column(db.Integer, db.ForeignKey('Artiste.artiste_id'))
