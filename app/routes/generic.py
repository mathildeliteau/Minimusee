# imports des modules et des données nécessaires
from ..app import app, db, login_manager
from flask import render_template, redirect, flash, request, url_for
from ..models.donnees import *
from ..models.users import *
from flask_login import current_user, login_user, logout_user, login_required
from ..constantes import *

@app.route("/")
@app.route("/accueil")
def accueil():
    """ Route permettant l'affichage d'une page accueil
    """
    # On a bien sûr aussi modifié le template pour refléter le changement
    artistes = Artiste.query.order_by(Artiste.artiste_id.desc()).limit(20).all()

    return render_template("pages/accueil.html", artistes=artistes, titre="Accueil")

@login_required
@app.route("/insertion_lieu", methods=["GET", "POST"])
def insertion_lieu():
    """ Route permettant l'insertion d'un nouveau lieu
        """
    if request.method == "POST":
        statut, donnees = Lieu.insertion_lieu(
            nom=request.form.get("nom", None),
            ville=request.form.get("ville", None),
            pays=request.form.get("pays", None)
        )
        if statut is True:
            flash("Enregistrement effectué", "success")
            return redirect(url_for("insertion_lieu"))
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/insertion_lieu.html", titre="Insertion d'un lieu")
    else:
        return render_template("pages/insertion_lieu.html", titre="Insertion d'un lieu")


@login_required
@app.route("/insertion_artiste", methods=["GET", "POST"])
def insertion_artiste():
    """ Route permettant l'insertion d'un nouvel artiste
            """
    if request.method == "POST":
        statut, donnees = Artiste.insertion_artiste(
            nom=request.form.get("nom", None),
            date_mort=request.form.get("deces", None),
            date_naissance=request.form.get("naissance", None),
            activite=request.form.get("activite", None)
        )
        if statut is True:
            flash("Enregistrement effectué", "success")
            return redirect(url_for("insertion_artiste"))
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/insertion_artiste.html", titre="Insertion d'un artiste")
    else:
        return render_template("pages/insertion_artiste.html", titre="Insertion d'un artiste")

@login_required
@app.route("/insertion_oeuvre", methods=["GET", "POST"])
def insertion_oeuvre():
    """ Route permettant l'insertion d'une nouvelle oeuvre
            """
    lieux = Lieu.query.all()
    artistes = Artiste.query.all()
    if request.method == "POST":
        statut, donnees = Oeuvre.insertion_oeuvre(
            titre=request.form.get("titre", None),
            creation=request.form.get("creation", None),
            id_lieu=request.form.get("lieu", None),
            ids_artistes=request.form.getlist("artiste", None)
        )
        if statut is True:
            flash("Enregistrement effectué", "success")
            return redirect(url_for("insertion_oeuvre"))
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/insertion_oeuvre.html", titre="Insertion d'une oeuvre", lieux=lieux, artistes=artistes)
    else:
        return render_template("pages/insertion_oeuvre.html", titre="Insertion d'une oeuvre", lieux=lieux, artistes=artistes)


@app.route("/register", methods=["GET", "POST"])
def inscription():
    """ Route gérant les inscriptions
    """
    # Si on est en POST, cela veut dire que le formulaire a été envoyé
    if request.method == "POST":
        statut, donnees = User.creer(
            login=request.form.get("login", None),
            email=request.form.get("email", None),
            nom=request.form.get("nom", None),
            prenom=request.form.get("prénom", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if statut is True:
            flash("Enregistrement effectué. Identifiez-vous maintenant", "success")
            return redirect("/")
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/inscription.html")
    else:
        return render_template("pages/inscription.html")


@app.route("/connexion", methods=["POST", "GET"])
def connexion():
    """ Route gérant les connexions
    """
    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connecté(e)", "info")
        return redirect("/")
    # Si on est en POST, cela veut dire que le formulaire a été envoyé
    if request.method == "POST":
        utilisateur = User.identification(
            login=request.form.get("login", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if utilisateur:
            flash("Connexion effectuée", "success")
            login_user(utilisateur)
            return redirect("/")
        else:
            flash("Les identifiants n'ont pas été reconnus", "error")

    return render_template("pages/connexion.html")
login_manager.login_view = 'connexion'


@app.route("/deconnexion", methods=["POST", "GET"])
def deconnexion():
    """Route gérant la déconnexion
    """
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté(e)", "info")
    return redirect("/")

@login_required
@app.route("/fiche_oeuvre/<int:id_oeuvre>", methods=["POST", "GET"])
def fiche_oeuvre(id_oeuvre):
    """ Route permettant l'affichage de la fiche d'une oeuvre
                """
    oeuvre = Oeuvre.query.filter(Oeuvre.oeuvre_id == id_oeuvre).first()
    lieu = Lieu.query.filter(Lieu.lieu_id == oeuvre.lieu_conservation).first()
    # récupération des id des artistes; .all() car il y en a plusieurs
    # création de la liste
    artistes = [Artiste.query.filter(Artiste.artiste_id == artiste.artiste_id).first() for artiste in
                Oeuvre_artiste.query.filter(Oeuvre_artiste.oeuvre_id == oeuvre.oeuvre_id).all()]

    if request.method=="POST":
        statut, donnees = Oeuvre.suppression_oeuvre(
            id_oeuvre=int(id_oeuvre)
        )
        if statut is True:
            flash("Suppression effectuée", "success")
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")

    return render_template("pages/fiche_oeuvre.html", titre=oeuvre.oeuvre_titre, oeuvre=oeuvre, lieu=lieu, artistes=artistes)

@login_required
@app.route("/fiche_artiste/<int:id_artiste>", methods=["POST", "GET"])
def fiche_artiste(id_artiste):
    """ Route permettant l'affichage de la fiche d'un artiste
                    """
    artiste = Artiste.query.filter(Artiste.artiste_id == id_artiste).first()
    oeuvres = [Oeuvre.query.filter(Oeuvre.oeuvre_id == oeuvre.oeuvre_id).first() for oeuvre in Oeuvre_artiste.query.filter(id_artiste==Oeuvre_artiste.artiste_id).all()]
    if request.method=="POST":
        statut, donnees = Artiste.suppression_artiste(
            id_artiste=int(id_artiste)
        )
        if statut is True:
            flash("Suppression effectuée", "success")
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
    return render_template("pages/fiche_artiste.html", titre=artiste.artiste_nom, artiste=artiste, oeuvres=oeuvres)

@login_required
@app.route("/fiche_lieu/<int:id_lieu>", methods=["POST", "GET"])
def fiche_lieu(id_lieu):
    """ Route permettant l'affichage de la fiche d'un lieu
                    """
    lieu = Lieu.query.filter(Lieu.lieu_id == id_lieu).first()
    oeuvres = Oeuvre.query.filter(Oeuvre.lieu_conservation == id_lieu).all()
    if request.method=="POST":
        statut, donnees = Lieu.supprimer_lieu(
            id_lieu=int(id_lieu)
        )
        if statut is True:
            flash("Suppression effectuée", "success")
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
    return render_template("pages/fiche_lieu.html", lieu=lieu, oeuvres=oeuvres)

@login_required
@app.route("/modifier_oeuvre/<int:id_oeuvre>", methods=["GET", "POST"])
def modifier_oeuvre(id_oeuvre):
    """ Route permettant la modification de la fiche d'une oeuvre
                    """
    lieux = Lieu.query.all()
    artistes = Artiste.query.all()
    # récupération de l'oeuvre et ses informations avant de cliquer sur modifier
    oeuvre = Oeuvre.query.filter(Oeuvre.oeuvre_id == id_oeuvre).first()
    lieu = Lieu.query.filter(Lieu.lieu_id == oeuvre.lieu_conservation).first()
    # récupération des id des artistes; .all() car il y en a plusieurs
    # création de la liste
    artistes_oeuvres = [Artiste.query.filter(Artiste.artiste_id == artiste.artiste_id).first() for artiste in
                Oeuvre_artiste.query.filter(Oeuvre_artiste.oeuvre_id == oeuvre.oeuvre_id).all()]
    # On clique sur modifier
    if request.method == "POST":
        statut, donnees = Oeuvre.modification_oeuvre(
            titre=request.form.get("titre", None),
            creation=request.form.get("creation", None),
            id_lieu=request.form.get("lieu", None),
            ids_artistes=request.form.getlist("artiste", None),
            id_oeuvre=id_oeuvre
        )
        if statut is True:
            flash("Modification effectué", "success")
            return redirect(url_for("modifier_oeuvre", id_oeuvre=id_oeuvre))
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/modifier_oeuvre.html", titre="Modification d'une oeuvre", lieux=lieux, artistes=artistes, oeuvre=oeuvre, artistes_oeuvres=artistes_oeuvres, lieu=lieu)
    else:
        return render_template("pages/modifier_oeuvre.html", titre="Modification d'une oeuvre", lieux=lieux, artistes=artistes, oeuvre=oeuvre, artistes_oeuvres=artistes_oeuvres, lieu=lieu)

@login_required
@app.route("/modifier_artiste/<int:id_artiste>", methods=["GET", "POST"])
def modifier_artiste(id_artiste):
    """ Route permettant la modification de la fiche d'un artiste
                        """
    oeuvres = Oeuvre.query.all()
    # récupération de l'artiste et ses informations avant de cliquer sur modifier
    artiste = Artiste.query.filter(Artiste.artiste_id == id_artiste).first()
    # récupération des id des oeuvres; .all() car il y en a plusieurs
    # création de la liste
    oeuvres_artistes = [Oeuvre.query.filter(Oeuvre.oeuvre_id == oeuvre.oeuvre_id).first() for oeuvre in
                Oeuvre_artiste.query.filter(Oeuvre_artiste.artiste_id == artiste.artiste_id).all()]
    # On clique sur modifier
    if request.method == "POST":
        statut, donnees = Artiste.modification_artiste(
            nom=request.form.get("nom", None),
            date_naissance=request.form.get("naissance", None),
            date_mort=request.form.get("deces", None),
            activite=request.form.get("activite", None),
            ids_oeuvres=request.form.getlist("oeuvre", None),
            id_artiste=id_artiste
        )
        if statut is True:
            flash("Modification effectuée", "success")
            return redirect(url_for("modifier_artiste", id_artiste=id_artiste))
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/modifier_artiste.html", titre="Modification d'un artiste", artiste=artiste, oeuvres=oeuvres, oeuvres_artistes=oeuvres_artistes)
    else:
        return render_template("pages/modifier_artiste.html", titre="Modification d'un artiste", artiste=artiste, oeuvres=oeuvres, oeuvres_artistes=oeuvres_artistes)

@login_required
@app.route("/modifier_lieu/<int:id_lieu>", methods=["GET", "POST"])
def modifier_lieu(id_lieu):
    """ Route permettant la modification de la fiche d'un lieu
                        """
    # récupération du lieu et ses informations avant de cliquer sur modifier
    lieu = Lieu.query.filter(Lieu.lieu_id == id_lieu).first()
    # récupération des id des oeuvres; .all() car il y en a plusieurs
    # création de la liste
    oeuvres = [Oeuvre.query.filter(Oeuvre.oeuvre_id == oeuvre.oeuvre_id).first() for oeuvre in
                Oeuvre.query.filter(Oeuvre.lieu_conservation == lieu.lieu_id).all()]
    # On clique sur modifier
    if request.method == "POST":
        statut, donnees = Lieu.modification_lieu(
            nom=request.form.get("nom", None),
            ville=request.form.get("ville", None),
            pays=request.form.get("pays", None),
            id_lieu=id_lieu
        )
        if statut is True:
            flash("Modification effectuée", "success")
            return redirect(url_for("modifier_lieu", id_lieu=id_lieu))
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/modifier_lieu.html", titre="Modification d'un lieu", lieu=lieu, oeuvres=oeuvres)
    else:
        return render_template("pages/modifier_lieu.html", titre="Modification d'un lieu", lieu=lieu, oeuvres=oeuvres)

@app.route("/recherche")
def recherche():
    """ Route permettant la recherche plein-texte
    """
    # On préfèrera l'utilisation de .get() ici
    # qui permet d'éviter un if long (if "clef" in dictionnaire and dictonnaire["clef"])
    motclef = request.args.get("keyword", None)
    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1

    # On crée une liste vide de résultats (qui restera vide par défaut
    # si on n'a pas de mot-clef)
    resultats = []

    # On fait de même pour le titre de la page
    titre = "Recherche"
    # si l'utilisateur entre un mot-clef, on fait la requête dans la table Oeuvre
    if motclef:
        resultats = Oeuvre.query.filter(
            Oeuvre.oeuvre_titre.like("%{}%".format(motclef))
        ).paginate(page=page, per_page=RESULTATS_PAR_PAGE)
        titre = "Résultat pour la recherche `" + motclef + "`"
    # on retourne la page de recherche avec le résultat de la requête
    return render_template(
        "pages/recherche.html",
        resultats=resultats,
        titre=titre,
        keyword=motclef
    )
