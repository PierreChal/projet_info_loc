# controller/client_controller.py
# ce fichier est responsable de la gestion des clients dans l'application
# il fait partie de l'architecture MVC (modèle-vue-contrôleur)
#
# structure:
# - importe le modèle client et la classe database
# - définit la classe clientcontroller avec méthodes pour créer, modifier, supprimer et rechercher des clients
# - fait le lien entre les vues (interfaces utilisateur) et le modèle de données
# - gère la validation des données et la logique métier
#
# interactions:
# - utilise le modèle client pour représenter les données
# - communique avec la base de données via la classe database
# - reçoit les requêtes des vues et renvoie les résultats
# - gère les erreurs et exceptions

from model.client import Client
from utils.database import Database


class ClientController:
    """
    contrôleur pour gérer les opérations liées aux clients.
    fait le lien entre la vue et le modèle client.

    attributes:
        db (database): instance de la base de données

    author:
        [votre nom]
    """

    def __init__(self, db):
        """
        initialise le contrôleur avec une connexion à la base de données.

        args:
            db (database): instance de la base de données
        """
        self.db = db

    def creer_client(self, nom, prenom, adresse, telephone, email):
        """
        crée un nouveau client dans le système.

        args:
            nom (str): nom du client
            prenom (str): prénom du client
            adresse (str): adresse postale
            telephone (str): numéro de téléphone
            email (str): adresse email

        returns:
            client: client créé, ou none en cas d'erreur
        """
        try:
            # validation des données
            if not self._valider_donnees_client(nom, prenom, adresse, telephone, email):
                return None

            # création de l'objet client (sans id pour l'instant)
            nouveau_client = Client(
                id=None,
                nom=nom,
                prenom=prenom,
                adresse=adresse,
                telephone=telephone,
                email=email
            )

            # sauvegarde dans la base de données
            client_id = self.db.sauvegarder_client(nouveau_client)

            # récupération du client complet depuis la base de données
            return self.db.charger_client(client_id)

        except Exception as e:
            print(f"erreur lors de la création du client: {e}")
            return None

    def charger_client(self, id):
        try:
            return self.db.charger_client(id)
        except Exception as e:
            print(e)
            return None

    def modifier_client(self, client_id, **kwargs):
        """
        modifie les informations d'un client existant.

        args:
            client_id (int): id du client à modifier
            **kwargs: attributs à modifier (nom, prenom, adresse, telephone, email)

        returns:
            client: client modifié, ou none en cas d'erreur
        """
        try:
            # chargement du client existant
            client = self.db.charger_client(client_id)
            if not client:
                return None

            # mise à jour des attributs fournis
            if 'nom' in kwargs:
                client.nom = kwargs['nom']
            if 'prenom' in kwargs:
                client.prenom = kwargs['prenom']
            if 'adresse' in kwargs:
                client.adresse = kwargs['adresse']
            if 'telephone' in kwargs:
                client.telephone = kwargs['telephone']
            if 'email' in kwargs:
                client.email = kwargs['email']

            # sauvegarde des modifications
            self.db.sauvegarder_client(client)

            # récupération du client mis à jour
            return self.db.charger_client(client_id)

        except Exception as e:
            print(f"erreur lors de la modification du client: {e}")
            return None

    def supprimer_client(self, client_id):
        """
        supprime un client du système.

        args:
            client_id (int): id du client à supprimer

        returns:
            bool: true si la suppression a réussi, false sinon
        """
        try:
            # vérification que le client n'a pas de réservations actives
            client = self.db.charger_client(client_id)
            if not client:
                return False

            reservations_actives = [r for r in client.historique_reservations
                                    if r.statut == "confirmée"]

            if reservations_actives:
                print("impossible de supprimer un client ayant des réservations actives")
                return False

            # suppression du client
            return self.db.supprimer_client(client_id)

        except Exception as e:
            print(f"erreur lors de la suppression du client: {e}")
            return False

    def rechercher_clients(self, criteres=None):
        """
        recherche des clients selon certains critères.

        args:
            criteres (dict, optional): critères de recherche (nom, prénom, email, etc.)

        returns:
            list: liste des clients correspondant aux critères
        """
        try:
            return self.db.rechercher_clients(criteres)
        except Exception as e:
            print(f"erreur lors de la recherche de clients: {e}")
            return []


    def lister_tous_clients(self):
        """
        Récupère tous les clients de la base de données

        Returns:
            list: Liste des objets Client
        """
        try:
            return self.db.lister_clients()  # ou la méthode équivalente dans ta DB
        except Exception as e:
            print(f"Erreur lors de la récupération des clients: {e}")
            return []

    def obtenir_client(self, client_id):
        """
        récupère un client par son id.

        args:
            client_id (int): id du client à récupérer

        returns:
            client: client trouvé, ou none si non trouvé
        """
        try:
            return self.db.charger_client(client_id)
        except Exception as e:
            print(f"erreur lors de la récupération du client: {e}")
            return None

    def obtenir_reservations_client(self, client_id):
        """
        récupère toutes les réservations d'un client.

        args:
            client_id (int): id du client

        returns:
            dict: dictionnaire contenant les réservations par statut
        """
        try:
            client = self.db.charger_client(client_id)
            if not client:
                return {}

            # organisation des réservations par statut
            reservations_par_statut = {
                "confirmées": client.obtenir_reservations_en_cours(),
                "passées": client.obtenir_reservations_passees(),
                "annulées": [r for r in client.historique_reservations if r.statut == "annulée"]
            }

            return reservations_par_statut

        except Exception as e:
            print(f"erreur lors de la récupération des réservations: {e}")
            return {}

    def _valider_donnees_client(self, nom, prenom, adresse, telephone, email):
        """
        valide les données d'un client.

        args:
            nom (str): nom du client
            prenom (str): prénom du client
            adresse (str): adresse postale
            telephone (str): numéro de téléphone
            email (str): adresse email

        returns:
            bool: true si les données sont valides, false sinon
        """
        # vérification des champs obligatoires
        if not nom or not prenom or not adresse or not telephone or not email:
            print("tous les champs sont obligatoires")
            return False

        # validation simple du format de l'email
        if "@" not in email or "." not in email:
            print("format d'email invalide")
            return False

        # validation simple du format du téléphone (à adapter selon le pays)
        if not all(c.isdigit() or c in " .-" for c in telephone):
            print("format de téléphone invalide")
            return False

        return True

# Exemple d'utilisation (ce code ne s'exécute que si on lance le fichier directement)
if __name__ == "__main__":
    # Création d'une instance de la base de données
    db = Database("test_client.db")

    # Création du contrôleur
    client_controller = ClientController(db)

    # Création d'un client
    nouveau_client = client_controller.creer_client(
        nom="Dupont",
        prenom="Jean",
        adresse="123 rue de la Paix, 75001 Paris",
        telephone="01 23 45 67 89",
        email="jean.dupont@example.com"
    )

    if nouveau_client:
        print(f"Client créé: {nouveau_client}")

        # Modification du client
        client_modifie = client_controller.modifier_client(
            nouveau_client.id,
            adresse="456 avenue des Champs-Élysées, 75008 Paris",
            telephone="06 12 34 56 78"
        )

        if client_modifie:
            print(f"Client modifié: {client_modifie}")

        # Recherche de clients
        clients = client_controller.rechercher_clients({"nom": "Dupont"})
        print(f"Clients trouvés: {len(clients)}")

    # Fermeture de la connexion à la base de données
    db.fermer()