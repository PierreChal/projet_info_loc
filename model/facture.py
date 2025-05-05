# model/facture.py
# on fait ici la classe Facture et le pattern Strategy pour la génération de documents

from datetime import datetime
from abc import ABC, abstractmethod


class Facture:
    """
    classe représentant une facture de reservation d'un véhicule

    Attributes:
        id (int): Identifiant unique de la facture
        reservation_id (int): ID de la réservation associée
        date_emission (datetime): Date d'émission de la facture
        montant_ht (float): Montant hors taxes
        taux_tva (float): Taux de TVA (ex: 0.2 pour 20%)
        montant_ttc (float): Montant TTC
    """

    def __init__(self, id, reservation_id, date_emission, montant_ht, taux_tva=0.2):
        """
        initialise une facture

        Args:
            id (int): Identifiant unique de la facture
            reservation_id (int): ID de la réservation associée
            date_emission (datetime): Date d'émission de la facture
            montant_ht (float): Montant hors taxes
            taux_tva (float, optional): Taux de TVA (défaut: 20%)
        """
        self.id = id
        self.reservation_id = reservation_id
        self.date_emission = date_emission
        self.montant_ht = montant_ht
        self.taux_tva = taux_tva

        # calcul automatique du montant TTC (avec TVA)
        self.montant_ttc = montant_ht * (1 + taux_tva)

    def generer_document(self, client, vehicule, reservation, format_document="pdf"):
        """
        Génère un document de facturation dans le format spécifié.
        Utilise le pattern Strategy pour sélectionner le générateur approprié.

        Args:
            client: Objet Client concerné
            vehicule: Objet Véhicule concerné
            reservation: Objet Réservation concerné
            format_document (str): Format du document ('pdf', 'html', 'txt')

        Returns:
            str: Chemin du fichier généré ou contenu du document
        """
        # stratégie selon le format demandé
        if format_document.lower() == "pdf":
            generateur = PDFDocumentStrategy()
        elif format_document.lower() == "html":
            generateur = HTMLDocumentStrategy()
        elif format_document.lower() == "txt":
            generateur = TexteDocumentStrategy()
        else:
            raise ValueError(f"Format non supporté: {format_document}")

        # utilisation de la stratégie
        return generateur.generer(self, client, vehicule, reservation)

    def calculer_details_tva(self):
        """
        Calcule les détails de TVA pour la facture.

        Returns:
            dict: Dictionnaire contenant les détails de TVA
        """
        montant_tva = self.montant_ht * self.taux_tva

        return {
            "taux_tva": self.taux_tva * 100,  # En pourcentage
            "base_ht": self.montant_ht,
            "montant_tva": montant_tva,
            "montant_ttc": self.montant_ttc
        }

    def __str__(self):
        """
        Représentation textuelle de la facture.
        """
        return (f"Facture #{self.id} - Réservation #{self.reservation_id} - "
                f"Émise le {self.date_emission.strftime('%d/%m/%Y')} - "
                f"Montant TTC: {self.montant_ttc:.2f} €")


# -----------------------------------------------------
# Implémentation du pattern Strategy pour la génération de documents
# -----------------------------------------------------

class DocumentStrategy(ABC):
    """
    Classe abstraite définissant l'interface pour les stratégies de génération de documents.
    Pattern Strategy: définit une famille d'algorithmes interchangeables.

    Author:
        [Votre nom]
    """

    @abstractmethod
    def generer(self, facture, client, vehicule, reservation):
        """
        Méthode abstraite pour générer un document.

        Args:
            facture (Facture): Facture à inclure dans le document
            client: Objet Client concerné
            vehicule: Objet Véhicule concerné
            reservation: Objet Réservation concerné

        Returns:
            str: Chemin du fichier généré ou contenu du document
        """
        pass


class PDFDocumentStrategy(DocumentStrategy):
    """
    Stratégie concrète pour générer un document PDF.

    Author:
        [Votre nom]
    """

    def generer(self, facture, client, vehicule, reservation):
        """
        Génère une facture au format PDF.

        Args:
            facture (Facture): Facture à inclure dans le document
            client: Objet Client concerné
            vehicule: Objet Véhicule concerné
            reservation: Objet Réservation concerné

        Returns:
            str: Chemin du fichier PDF généré
        """
        # Nom du fichier de sortie
        nom_fichier = f"facture_{facture.id}_{client.id}.pdf"

        # Dans une implémentation réelle, on utiliserait une bibliothèque comme
        # ReportLab pour générer le PDF. Pour cet exemple, on simule la génération.
        print(f"Génération du PDF pour la facture #{facture.id}...")

        # Simulation de génération PDF
        self._generer_en_tete(facture, client)
        self._generer_details_location(facture, vehicule, reservation)
        self._generer_tableau_montants(facture)
        self._generer_pied_page(facture)

        print(f"PDF généré avec succès: {nom_fichier}")

        return nom_fichier

    def _generer_en_tete(self, facture, client):
        """
        Génère l'en-tête du document PDF.
        """
        print("- Ajout de l'en-tête avec le logo de l'entreprise")
        print(f"- Informations client: {client.prenom} {client.nom}")
        print(f"- Date d'émission: {facture.date_emission.strftime('%d/%m/%Y')}")
        print(f"- Facture n°: {facture.id}")

    def _generer_details_location(self, facture, vehicule, reservation):
        """
        Génère la section des détails de location.
        """
        print("- Ajout des détails de la location:")
        print(f"  * Véhicule: {vehicule.marque} {vehicule.modele}")
        print(
            f"  * Période: du {reservation.date_debut.strftime('%d/%m/%Y')} au {reservation.date_fin.strftime('%d/%m/%Y')}")
        print(f"  * Durée: {reservation.duree_en_jours()} jours")

    def _generer_tableau_montants(self, facture):
        """
        Génère le tableau des montants.
        """
        details_tva = facture.calculer_details_tva()

        print("- Ajout du tableau des montants:")
        print(f"  * Montant HT: {details_tva['base_ht']:.2f} €")
        print(f"  * TVA ({details_tva['taux_tva']}%): {details_tva['montant_tva']:.2f} €")
        print(f"  * Montant TTC: {details_tva['montant_ttc']:.2f} €")

    def _generer_pied_page(self, facture):
        """
        Génère le pied de page.
        """
        print("- Ajout du pied de page avec les mentions légales")
        print("- Ajout des conditions de paiement")


class HTMLDocumentStrategy(DocumentStrategy):
    """
    Stratégie concrète pour générer un document HTML.

    Author:
        [Votre nom]
    """

    def generer(self, facture, client, vehicule, reservation):
        """
        Génère une facture au format HTML.

        Args:
            facture (Facture): Facture à inclure dans le document
            client: Objet Client concerné
            vehicule: Objet Véhicule concerné
            reservation: Objet Réservation concerné

        Returns:
            str: Contenu HTML de la facture
        """
        # Dans une implémentation réelle, on génèrerait un véritable HTML
        # Pour cet exemple, on retourne simplement une structure HTML basique

        details_tva = facture.calculer_details_tva()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Facture #{facture.id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ display: flex; justify-content: space-between; }}
                .company {{ font-weight: bold; font-size: 24px; }}
                .details {{ margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                .total {{ font-weight: bold; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company">Location de Véhicules</div>
                <div>
                    <h2>FACTURE</h2>
                    <p>N° {facture.id}</p>
                    <p>Date: {facture.date_emission.strftime('%d/%m/%Y')}</p>
                </div>
            </div>

            <div class="client-info">
                <h3>Client</h3>
                <p>{client.prenom} {client.nom}<br>
                {client.adresse}<br>
                {client.email}<br>
                {client.telephone}</p>
            </div>

            <div class="details">
                <h3>Détails de la location</h3>
                <p>Véhicule: {vehicule.marque} {vehicule.modele} ({vehicule.annee})</p>
                <p>Période: du {reservation.date_debut.strftime('%d/%m/%Y')} au {reservation.date_fin.strftime('%d/%m/%Y')}</p>
                <p>Durée: {reservation.duree_en_jours()} jours</p>
            </div>

            <table>
                <tr>
                    <th>Description</th>
                    <th>Montant HT</th>
                    <th>TVA</th>
                    <th>Montant TTC</th>
                </tr>
                <tr>
                    <td>Location de véhicule</td>
                    <td>{details_tva['base_ht']:.2f} €</td>
                    <td>{details_tva['montant_tva']:.2f} €</td>
                    <td>{details_tva['montant_ttc']:.2f} €</td>
                </tr>
                <tr class="total">
                    <td colspan="3">Total</td>
                    <td>{details_tva['montant_ttc']:.2f} €</td>
                </tr>
            </table>

            <div class="footer">
                <p>Merci de votre confiance.</p>
                <p>Location de Véhicules - 123 rue des Voitures - 75000 Paris</p>
                <p>SIRET: 123 456 789 00012 - TVA: FR12 123 456 789</p>
            </div>
        </body>
        </html>
        """

        return html


class TexteDocumentStrategy(DocumentStrategy):
    """
    Stratégie concrète pour générer un document texte simple.

    Author:
        [Votre nom]
    """

    def generer(self, facture, client, vehicule, reservation):
        """
        Génère une facture au format texte.

        Args:
            facture (Facture): Facture à inclure dans le document
            client: Objet Client concerné
            vehicule: Objet Véhicule concerné
            reservation: Objet Réservation concerné

        Returns:
            str: Contenu texte de la facture
        """
        details_tva = facture.calculer_details_tva()

        # Création d'une représentation textuelle simple
        texte = []
        texte.append("=" * 60)
        texte.append("                    FACTURE                    ")
        texte.append("=" * 60)
        texte.append(f"Facture n° : {facture.id}")
        texte.append(f"Date : {facture.date_emission.strftime('%d/%m/%Y')}")
        texte.append("")

        texte.append("INFORMATIONS CLIENT")
        texte.append("-" * 60)
        texte.append(f"Nom : {client.prenom} {client.nom}")
        texte.append(f"Adresse : {client.adresse}")
        texte.append(f"Email : {client.email}")
        texte.append(f"Téléphone : {client.telephone}")
        texte.append("")

        texte.append("DÉTAILS DE LA LOCATION")
        texte.append("-" * 60)
        texte.append(f"Véhicule : {vehicule.marque} {vehicule.modele} ({vehicule.annee})")
        texte.append(
            f"Période : du {reservation.date_debut.strftime('%d/%m/%Y')} au {reservation.date_fin.strftime('%d/%m/%Y')}")
        texte.append(f"Durée : {reservation.duree_en_jours()} jours")
        texte.append("")

        texte.append("MONTANTS")
        texte.append("-" * 60)
        texte.append(f"Montant HT : {details_tva['base_ht']:.2f} €")
        texte.append(f"TVA ({details_tva['taux_tva']}%) : {details_tva['montant_tva']:.2f} €")
        texte.append(f"Montant TTC : {details_tva['montant_ttc']:.2f} €")
        texte.append("")

        texte.append("=" * 60)
        texte.append("Merci de votre confiance.")
        texte.append("Location de Véhicules - 123 rue des Voitures - 75000 Paris")
        texte.append("SIRET: 123 456 789 00012 - TVA: FR12 123 456 789")

        return "\n".join(texte)


# Exemple d'utilisation (ce code ne s'exécute que si on lance le fichier directement)
if __name__ == "__main__":
    # Import nécessaire pour l'exemple
    from datetime import datetime, timedelta

    # Création d'une facture
    facture = Facture(
        id=1,
        reservation_id=101,
        date_emission=datetime.now(),
        montant_ht=250.0,
        taux_tva=0.2
    )

    print(facture)


    # Création d'objets fictifs pour tester la génération de documents
    class ClientTest:
        def __init__(self):
            self.id = 1
            self.prenom = "Jean"
            self.nom = "Dupont"
            self.adresse = "123 rue de la Paix, 75001 Paris"
            self.email = "jean.dupont@example.com"
            self.telephone = "01 23 45 67 89"


    class VehiculeTest:
        def __init__(self):
            self.id = 1
            self.marque = "Renault"
            self.modele = "Clio"
            self.annee = 2020


    class ReservationTest:
        def __init__(self):
            self.id = 101
            self.date_debut = datetime.now()
            self.date_fin = datetime.now() + timedelta(days=5)

        def duree_en_jours(self):
            return 6  # Exemple simplifié


    # Création des objets de test
    client = ClientTest()
    vehicule = VehiculeTest()
    reservation = ReservationTest()

    # Test de génération au format texte
    print("\nGénération au format texte:")
    texte = facture.generer_document(client, vehicule, reservation, "txt")
    print(texte)

    # Test de génération au format PDF (simulé)
    print("\nGénération au format PDF:")
    pdf = facture.generer_document(client, vehicule, reservation, "pdf")

    # Test de génération au format HTML
    print("\nGénération au format HTML (extrait):")
    html = facture.generer_document(client, vehicule, reservation, "html")
    print(html[:500] + "...")  # Affichage du début du HTML seulement