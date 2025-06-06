# model/vehicule.py
# ce fichier implémente la hiérarchie des classes de véhicules du système de location
# il fait partie de l'architecture MVC (modèle-vue-contrôleur)
#
# structure:
# - définit une classe abstraite Vehicule avec les attributs et méthodes communs
# - implémente trois classes dérivées : Voiture, Utilitaire et Moto
# - utilise le polymorphisme pour les méthodes comme calculer_tarif_journalier
# - fournit des méthodes de calcul de coûts et d'affichage adaptées à chaque type
#
# interactions:
# - utilisé par le ParcController pour gérer les différents types de véhicules
# - interagit avec la classe Reservation pour les calculs de prix
# - sert de modèle de base pour représenter tous les véhicules du système
# - permet l'extension facile à de nouveaux types de véhicules si nécessaire

from abc import ABC, abstractmethod


# ABC = Abstract Base Class, permet de créer des classes abstraites en Python
# abstractmethod est un décorateur pour définir des méthodes abstraites

class Vehicule(ABC):
    """
    classe abstraite qui permet de definir les attributs commun à tous les véhicules
    attention on ne pourra pas instancier cette classe car elle est abstraite
    c'est en quelques sorte la classe mère des voiture/utilitaire et moto

    Attributes:
        id (int): Identifiant unique du véhicule
        marque (str): Marque du véhicule
        modele (str): Modèle du véhicule
        annee (int): Année de mise en circulation
        kilometrage (int): Kilométrage actuel
        prix_achat (float): Prix d'achat du véhicule
        cout_entretien_annuel (float): Coût annuel d'entretien
        categorie (str): Catégorie du véhicule
    """

    def __init__(self, id, marque, modele, annee, kilometrage, prix_achat, cout_entretien_annuel, categorie):
        """
        Initialise un nouveau véhicule avec les attributs de base.
        """
        # les attributs sont pris sur les paramètre du même nom, c'est plus clair comme ca
        self.id = id
        self.marque = marque
        self.modele = modele
        self.annee = annee
        self.kilometrage = kilometrage
        self.prix_achat = prix_achat
        self.cout_entretien_annuel = cout_entretien_annuel
        self.categorie = categorie

    def calculer_cout_possession(self, annees):
        """
        on définit une méthode ici pour calculer le cout après l'achat d'un véhicule sur 5 ans
        en ajoutant les couts propres d'entretiens (annuels) de chaque véhicule qui sont des attributs

        Args:
            annees (int): Nombre d'années à considérer

        Returns:
            float: Coût total de possession
        """
        # on considère un amortissement linéaire sur 5 ans
        amortissement_annuel = self.prix_achat / 5

        # pour les 5 premières années, on compte l'amortissement + l'entretien
        if annees <= 5:
            cout_total = (amortissement_annuel + self.cout_entretien_annuel) * annees
        else:
            # après 5 ans, le véhicule est totalement amorti (selon nos critères arbitraires), on ne compte que l'entretien
            cout_5_premieres_annees = (amortissement_annuel + self.cout_entretien_annuel) * 5
            cout_annees_suivantes = self.cout_entretien_annuel * (annees - 5)
            cout_total = cout_5_premieres_annees + cout_annees_suivantes

        return cout_total

    @abstractmethod
    def calculer_tarif_journalier(self):
        """
        méthode abstraite pour calculer le tarif journalier de location
        on fait de la polymorphisation, il faut donc définir cette méthodes dans les classes dérivées/filles

        Returns:
            float: Tarif journalier en euros
        """
        # pas d'implémentation dans la classe abstraite
        # doit être définie dans chaque classe dérivée
        pass

    def __str__(self):
        """
        donne une représentation textuelle du véhicule
        c'est utile partout pour simplement faire un affichage propre avec le f-string
        """
        return f"{self.marque} {self.modele} ({self.annee}) - {self.kilometrage} km"


class Voiture(Vehicule):
    """
    classe représentant une voiture de location
    Héritage de véhicule

    Attributes additionnels:
        nb_places (int): Nombre de places assises
        puissance (int): Puissance en chevaux
        carburant (str): Type de carburant (essence, diesel, électrique...)
        options (list): Liste des options disponibles
    """

    def __init__(self, id, marque, modele, annee, kilometrage, prix_achat, cout_entretien_annuel,
                 nb_places, puissance, carburant, options=None):
        """
        on y met les attributs qui sont utiles pour les méthodes et ce que l'on veut modéliser
        """
        # appel du constructeur super de la classe parente (Vehicule)
        super().__init__(id, marque, modele, annee, kilometrage, prix_achat, cout_entretien_annuel, "Voiture")

        #spécificité de la classe Voiture
        self.nb_places = nb_places
        self.puissance = puissance
        self.carburant = carburant

        # on initialise avec une liste vide si pas d'option pour la voiture
        if options is None:
            self.options = []
        else:
            self.options = options

    def calculer_tarif_journalier(self):
        """
        on a choisi de faire un calcul journalier selon la puissance du véhicule

        Returns:
            float: Tarif journalier en euros
        """
        # tarif selon nos valeurs qui sont choisies complètement arbitrairement par nos soins
        if self.puissance < 100:
            # petite cylindrée (moins de 100 chevaux), ma voiture par exemple
            tarif_base = 40
        elif self.puissance < 150:
            # moyenne cylindrée
            tarif_base = 60
        else:
            # GROSSE cylindrée (150 chevaux et plus), pour aller très vite en vacances par exemple
            tarif_base = 80

        # on ajoute 5 euros pour chaque option
        majoration_options = len(self.options) * 5

        # le tarif final est la somme du tarif avec le prix des majorations
        return tarif_base + majoration_options

    def ajouter_option(self, option):
        """
        nous permet de d'ajouter une option dans les attributs de la voiture

        Args:
            option (str): Nom de l'option à ajouter
        """
        if option not in self.options:
            self.options.append(option)

    def __str__(self):
        """
        mise en forme texte des attributs intéressant à écrire
        """
        # en utilisant le  __str__ de la classe mère (véhicule) et on ajoute nos informations propre à voiture
        return f"{super().__str__()} - {self.puissance} ch - {self.carburant} - {self.nb_places} places"


class Utilitaire(Vehicule):
    """
    on introduit une autre classe fille sous le même procédé en prenant en compte les spécificité d'un utilitaire

    Attributes additionnels:
        volume (float): Volume utile en m³
        charge_utile (float): Charge maximale en kg
        hayon (bool): Présence d'un hayon élévateur
    """

    def __init__(self, id, marque, modele, annee, kilometrage, prix_achat, cout_entretien_annuel,
                 volume, charge_utile, hayon=False):
        """
        Initialise l'utilitaire en héritage avec le constructeur
        """
        super().__init__(id, marque, modele, annee, kilometrage, prix_achat, cout_entretien_annuel, "Utilitaire")

        self.volume = volume  # en mètres cubes critère pour les utilitaires
        self.charge_utile = charge_utile  # en kg
        self.hayon = hayon  # booléen (True/False), c'est l'espèce de monte-charge intégré dans le véhicule

    def calculer_tarif_journalier(self):
        """
        idem

        Returns:
            float: Tarif journalier en euros
        """
        # tarif calculer par le volume
        if self.volume < 5:
            # petit utilitaire
            tarif_base = 50
        elif self.volume < 10:
            # utilitaire moyen
            tarif_base = 70
        else:
            # grand utilitaire
            tarif_base = 80

        # majoration de 10 pour le hayon élévateur (si présent)
        majoration_hayon = 10 if self.hayon else 0

        return tarif_base + majoration_hayon

    def __str__(self):
        """
        idem que pour voiture
        """
        hayon_info = "avec hayon" if self.hayon else "sans hayon"
        return f"{super().__str__()} - {self.volume} m³ - {self.charge_utile} kg - {hayon_info}"


class Moto(Vehicule):
    """
    idem pour la moto

    Attributes particuliers :
        cylindree (int): Cylindrée en cm³
        type (str): Type de moto (sportive, routière, trail...)
    """

    def __init__(self, id, marque, modele, annee, kilometrage, prix_achat, cout_entretien_annuel,
                 cylindree, type_moto):
        """
        Initialisation
        """
        # appel du constructeur de classe mère
        super().__init__(id, marque, modele, annee, kilometrage, prix_achat, cout_entretien_annuel, "Moto")

        # spécificité
        self.cylindree = cylindree  # en cm³
        self.type = type_moto  # sportive, routière, etc.

    def calculer_tarif_journalier(self):
        """
        calcul selon la cylindrée (équivalent de la puissance mais pour moto)

        Returns:
            float: Tarif journalier en euros
        """
        # le critère est la cylindrée ici
        if self.cylindree < 500:
            # petite
            return 30
        elif self.cylindree < 800:
            # moyenne
            return 40
        else:
            # grosse
            return 50

    def __str__(self):
        """
        idem que pour voiture
        """
        return f"{super().__str__()} - {self.cylindree} cm³ - {self.type}"


# exemple de ce fichier (n'est executé que si l'on RUN ce fichier)
if __name__ == "__main__":
    from datetime import datetime, timedelta
    from model.vehicule import Voiture, Utilitaire, Moto
    from utils.database import Database

    # Création d'une instance de la base de données
    db = Database("location.db")

    print("Ajout de véhicules dans la base de données...")

    # Création et ajout de voitures
    voiture1 = Voiture(
        id=None,
        marque="Citroen",
        modele="C3",
        annee=2007,
        kilometrage=115000,
        prix_achat=3000,
        cout_entretien_annuel=300,
        nb_places=5,
        puissance=65,
        carburant="Diesel",
        options=["Climatisation", "Radio"]
    )

    voiture2 = Voiture(
        id=None,
        marque="Renault",
        modele="Clio",
        annee=2020,
        kilometrage=15000,
        prix_achat=15000,
        cout_entretien_annuel=600,
        nb_places=5,
        puissance=90,
        carburant="Essence",
        options=["Climatisation", "GPS", "Bluetooth"]
    )

    voiture3 = Voiture(
        id=None,
        marque="Peugeot",
        modele="308",
        annee=2019,
        kilometrage=25000,
        prix_achat=18000,
        cout_entretien_annuel=800,
        nb_places=5,
        puissance=130,
        carburant="Diesel",
        options=["Climatisation", "GPS", "Régulateur", "Sièges chauffants"]
    )

    # Ajout des voitures
    voiture1_id = db.sauvegarder_vehicule(voiture1)
    voiture2_id = db.sauvegarder_vehicule(voiture2)
    voiture3_id = db.sauvegarder_vehicule(voiture3)
    print(f"Voitures ajoutées avec IDs: {voiture1_id}, {voiture2_id}, {voiture3_id}")

    # Création et ajout d'utilitaires
    utilitaire1 = Utilitaire(
        id=None,
        marque="Renault",
        modele="Master",
        annee=2019,
        kilometrage=30000,
        prix_achat=25000,
        cout_entretien_annuel=1500,
        volume=12,
        charge_utile=1200,
        hayon=True
    )

    utilitaire2 = Utilitaire(
        id=None,
        marque="Citroën",
        modele="Jumpy",
        annee=2018,
        kilometrage=45000,
        prix_achat=20000,
        cout_entretien_annuel=1200,
        volume=8,
        charge_utile=1000,
        hayon=False
    )

    # Ajout des utilitaires
    utilitaire1_id = db.sauvegarder_vehicule(utilitaire1)
    utilitaire2_id = db.sauvegarder_vehicule(utilitaire2)
    print(f"Utilitaires ajoutés avec IDs: {utilitaire1_id}, {utilitaire2_id}")

    # Création et ajout de motos
    moto1 = Moto(
        id=None,
        marque="Honda",
        modele="CB500F",
        annee=2020,
        kilometrage=8000,
        prix_achat=6000,
        cout_entretien_annuel=400,
        cylindree=500,
        type_moto="Roadster"
    )

    moto2 = Moto(
        id=None,
        marque="Yamaha",
        modele="MT-09",
        annee=2021,
        kilometrage=5000,
        prix_achat=9000,
        cout_entretien_annuel=500,
        cylindree=900,
        type_moto="Roadster"
    )

    # Ajout des motos
    moto1_id = db.sauvegarder_vehicule(moto1)
    moto2_id = db.sauvegarder_vehicule(moto2)
    print(f"Motos ajoutées avec IDs: {moto1_id}, {moto2_id}")

    print("Tous les véhicules ont été ajoutés avec succès dans la base de données.")

    # Fermeture de la connexion à la base de données
    db.fermer()