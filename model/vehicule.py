# contient la class vehicule et ses sous class

""" avec plusieurs attributs, on donne accès à ces
    dernier par les méthodes getter et les modifiers par les setters, cette partie peux être
    testée en bas.
    """

class Vehicule:
    """Classe représentant un véhicule générique."""

    _compteur_id = 1  # Compteur d'ID unique pour tous les véhicules

    def __init__(self, marque: str, modele: str, annee: int, prix_journalier: float, disponible: bool,
                 kilometrage: float):
        """Initialisation d'un véhicule avec un ID unique généré automatiquement."""
        self._id_vehicule = Vehicule._compteur_id
        Vehicule._compteur_id += 1  # Incrémentation du compteur d'ID

        self._marque = marque
        self._modele = modele
        self._annee = annee
        self._prix_journalier = prix_journalier
        self._disponible = disponible
        self._kilometrage = kilometrage

    # Propriétés (Getters)
    @property
    def id_vehicule(self):
        """Retourne l'ID unique du véhicule (lecture seule)."""
        return self._id_vehicule

    @property
    def marque(self):
        return self._marque

    @property
    def modele(self):
        return self._modele

    @property
    def annee(self):
        return self._annee

    @property
    def prix_journalier(self):
        return self._prix_journalier

    @property
    def disponible(self):
        return self._disponible

    @property
    def kilometrage(self):
        return self._kilometrage

    # Setters avec validation
    @prix_journalier.setter
    def prix_journalier(self, nouveau_prix: float):
        """Modifie le prix journalier avec validation."""
        if nouveau_prix < 0:
            raise ValueError("Le prix journalier ne peut pas être négatif.")
        self._prix_journalier = nouveau_prix

    @kilometrage.setter
    def kilometrage(self, nouveau_km: float):
        """Met à jour le kilométrage du véhicule avec validation."""
        if nouveau_km < self._kilometrage:
            raise ValueError("Le kilométrage ne peut pas être réduit.")
        self._kilometrage = nouveau_km

    def est_disponible(self) -> bool:
        """Retourne True si le véhicule est disponible, False sinon."""
        return self._disponible

    def changer_disponibilite(self, etat: bool):
        """Modifie l'état de disponibilité du véhicule."""
        self._disponible = etat

    def afficher_infos(self):
        """Affiche les détails du véhicule."""
        print(f"ID: {self._id_vehicule} | Marque: {self._marque} | Modèle: {self._modele} | "
              f"Année: {self._annee} | Prix: {self._prix_journalier}€/jour | "
              f"Disponible: {'Oui' if self._disponible else 'Non'} | Kilométrage: {self._kilometrage} km")

###############--------Sous classe voiture--------###############
""" On crée ici des sous classes de voiture avec super(), car les attributs de nos variables sont communs aux sous 
classes, de plus on a ajouter des attributs propre à chaque sous classes dont on pourra avoir accès avec les setters,
on a mis quelques conditions pour éviter les erreurs de rentrée de donnée.
"""

class Voiture(Vehicule):
    """Classe représentant une voiture, héritant de Véhicule."""

    def __init__(self, marque, modele, annee, prix_journalier, disponible, kilometrage, nb_places, type_moteur):
        super().__init__(marque, modele, annee, prix_journalier, disponible, kilometrage)
        self.nb_places = nb_places
        self.type_moteur = type_moteur

    @property
    def nb_places(self):
        return self._nb_places

    @nb_places.setter
    def nb_places(self, value):
        if value < 1:
            raise ValueError("Le nombre de places doit être au moins 1.")
        self._nb_places = value

    @property
    def type_moteur(self):
        return self._type_moteur

    @type_moteur.setter
    def type_moteur(self, value):
        moteurs_valides = {"Essence", "Diesel", "Électrique", "Hybride"}
        if value not in moteurs_valides:
            raise ValueError(f"Type de moteur invalide. Choisissez parmi {moteurs_valides}.")
        self._type_moteur = value


class Utilitaire(Vehicule):
    """Classe représentant un utilitaire, héritant de Véhicule."""

    def __init__(self, marque, modele, annee, prix_journalier, disponible, kilometrage, volume_m3):
        super().__init__(marque, modele, annee, prix_journalier, disponible, kilometrage)
        self.volume_m3 = volume_m3

    @property
    def volume_m3(self):
        return self._volume_m3

    @volume_m3.setter
    def volume_m3(self, value):
        if value < 0:
            raise ValueError("Le volume ne peut pas être négatif.")
        self._volume_m3 = value


class Moto(Vehicule):
    """Classe représentant une moto, héritant de Véhicule."""

    def __init__(self, marque, modele, annee, prix_journalier, disponible, kilometrage, cylindree):
        super().__init__(marque, modele, annee, prix_journalier, disponible, kilometrage)
        self.cylindree = cylindree

    @property
    def cylindree(self):
        return self._cylindree

    @cylindree.setter
    def cylindree(self, value):
        if value < 50:  # Exemple : Cylindrée minimale pour une moto
            raise ValueError("La cylindrée doit être d'au moins 50cc.")
        self._cylindree = value


# Exemple d'utilisation
if __name__ == "__main__":
    print("==== TEST DE LA VEHICULE ET SES SOUS CLASSES ====")

    # vehicule1 = Vehicule("Fiat", "Panda", 2012, 40.0, False, 25000)
    # vehicule2 = Vehicule("Citroen", "C3", 2007, 50.0, True, 110000)
    #
    # vehicule1.afficher_infos()
    # vehicule2.afficher_infos()
    #
    # # Tester les setters sécurisés
    # vehicule1.prix_journalier = 45.0
    # vehicule1.kilometrage = 25500
    # vehicule1.changer_disponibilite(False)
    #
    # vehicule1.afficher_infos()


    # voiture1 = Voiture("Toyota", "Yaris", 2022, 45.0, True, 15000, 5, "Hybride")
    # print(voiture1.nb_places)  # Lecture via @property
    # voiture1.nb_places = 4  # Modification sécurisée via @setter
    # print(voiture1.type_moteur)  # Lecture
    # voiture1.type_moteur = "Essence"  # Modification avec validation
    # # Si on essaie de mettre un moteur invalide :
    # try:
    #     voiture1.type_moteur = "Hydrogène"  # Erreur !
    # except ValueError as e:
    #     print("Erreur:", e)

    # contient la class vehicule et ses sous class, structure similaire au précedent

