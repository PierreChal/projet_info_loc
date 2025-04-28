# contient la class vehicule et ses sous class, structure similaire au précedent

class Client:
    _compteur_id = 1  # Génération automatique des IDs

    def __init__(self, nom, prenom, email, telephone):
        """Initialisation d'un client avec validation des données."""
        self._id_client = Client._compteur_id
        Client._compteur_id += 1

        self.nom = nom  # Utilisation des setters
        self.prenom = prenom
        self.email = email
        self.telephone = telephone
        self._historique_locations = []

    @property
    def id_client(self):
        return self._id_client

    @property
    def nom(self):
        return self._nom

    @nom.setter
    def nom(self, value):
        if not value or len(value) < 2:
            raise ValueError("Le nom doit contenir au moins 2 caractères.")
        self._nom = value

    @property
    def prenom(self):
        return self._prenom

    @prenom.setter
    def prenom(self, value):
        if not value or len(value) < 2:
            raise ValueError("Le prénom doit contenir au moins 2 caractères.")
        self._prenom = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        """Affecte directement l'email sans validation."""
        self._email = value

    @property
    def telephone(self):
        return self._telephone

    @telephone.setter
    def telephone(self, value):
        if not value.isdigit() or len(value) < 10:
            raise ValueError("Le numéro de téléphone doit contenir au moins 10 chiffres.")
        self._telephone = value

    @property
    def historique_locations(self):
        return self._historique_locations

    def afficher_infos(self):
        """Affiche les informations du client."""
        print(f"Client {self.id_client}: {self.prenom} {self.nom}, Email: {self.email}, Tel: {self.telephone}")

    def ajouter_location(self, location):
        """Ajoute une location à l’historique."""
        self._historique_locations.append(location)


# Exemple d'utilisation
if __name__ == "__main__":
    print("==== TEST DE LA CLASSE CLIENT ====")

    # client1 = Client("Dupont", "Jean", "jean.dupont@email.com", "0654321987")
    # client2 = Client("Martin", "Sophie", "sophie.martin@email.com", "0789546321")
    # client1.afficher_infos()
    # client2.afficher_infos()
    # client1.ajouter_location("Location de Renault Clio du 10/03/2025 au 12/03/2025")
    # client1.ajouter_location("Location de Peugeot 208 du 20/04/2025 au 25/04/2025")
    # client2.ajouter_location("Location de Moto Yamaha MT-07 du 05/05/2025 au 07/05/2025")
    # print("\nHistorique de locations de Jean Dupont :", client1.historique_locations)
    # print("Historique de locations de Sophie Martin :", client2.historique_locations)