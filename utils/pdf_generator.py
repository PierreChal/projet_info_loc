# utils/pdf_generator.py
# ce fichier implémente la génération de documents PDF pour les factures du système
# il fait partie des utilitaires de l'application dans l'architecture MVC
#
# structure:
# - utilise la bibliothèque ReportLab pour créer des documents PDF
# - définit la classe PDFGenerator avec des méthodes statiques pour la génération
# - décompose le document en sections logiques (en-tête, détails, tableau, pied de page)
# - gère la mise en forme avancée avec polices, couleurs et tableaux stylisés
#
# interactions:
# - utilisé par les contrôleurs ou les stratégies de génération de documents
# - dépend des modèles Facture, Client, Véhicule et Réservation pour les données
# - crée automatiquement le dossier de destination si nécessaire
# - produit des fichiers PDF de qualité professionnelle pour les factures clients

# importation de reportlab pour génération pdf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import cm
import os
from datetime import datetime


class PDFGenerator:
    """
    classe utilitaire pour génération pdf
    implémente création de pdf avec bibliothèque reportlab
    """

    @staticmethod
    def generer_facture(facture, client, vehicule, reservation, chemin_sortie=None):
        """
        génère facture en pdf

        args:
            facture: objet facture à inclure
            client: objet client concerné
            vehicule: objet véhicule concerné
            reservation: objet réservation concerné
            chemin_sortie: chemin de sauvegarde (optionnel)

        returns:
            str: chemin du fichier pdf généré
        """
        # chemin par défaut si non spécifié
        if chemin_sortie is None:
            # création dossier 'factures' si inexistant
            if not os.path.exists('factures'):
                os.makedirs('factures')

            # nom fichier basé sur id facture et date
            nom_fichier = f"factures/facture_{facture.id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        else:
            nom_fichier = chemin_sortie

        # création document pdf
        c = canvas.Canvas(nom_fichier, pagesize=A4)
        width, height = A4  # dimensions page a4

        # génération sections du document
        PDFGenerator._generer_en_tete(c, width, height, facture, client)
        PDFGenerator._generer_details_location(c, width, height, vehicule, reservation)
        PDFGenerator._generer_tableau_montants(c, width, height, facture)
        PDFGenerator._generer_pied_page(c, width, height)

        # finalisation et sauvegarde
        c.save()

        return nom_fichier

    @staticmethod
    def _generer_en_tete(c, width, height, facture, client):
        """
        génère en-tête du document

        args:
            c: canvas reportlab
            width: largeur page
            height: hauteur page
            facture: objet facture
            client: objet client
        """
        # en-tête avec logo entreprise (simulé)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(2 * cm, height - 2 * cm, "Location de Véhicules")

        # infos facture
        c.setFont("Helvetica-Bold", 14)
        c.drawString(width - 6 * cm, height - 2 * cm, "FACTURE")

        c.setFont("Helvetica", 10)
        c.drawString(width - 6 * cm, height - 2.5 * cm, f"N° {facture.id}")
        c.drawString(width - 6 * cm, height - 3 * cm, f"Date: {facture.date_emission.strftime('%d/%m/%Y')}")

        # rectangle décoratif
        c.setStrokeColor(colors.grey)
        c.rect(1 * cm, height - 3.5 * cm, width - 2 * cm, 0.1 * cm, fill=1)

        # infos client
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, height - 4.5 * cm, "Client")

        c.setFont("Helvetica", 10)
        c.drawString(2 * cm, height - 5.2 * cm, f"{client.prenom} {client.nom}")
        c.drawString(2 * cm, height - 5.7 * cm, client.adresse)
        c.drawString(2 * cm, height - 6.2 * cm, f"Email: {client.email}")
        c.drawString(2 * cm, height - 6.7 * cm, f"Tél: {client.telephone}")

    @staticmethod
    def _generer_details_location(c, width, height, vehicule, reservation):
        """
        génère section détails location

        args:
            c: canvas reportlab
            width: largeur page
            height: hauteur page
            vehicule: objet véhicule
            reservation: objet réservation
        """
        # titre section
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, height - 8 * cm, "Détails de la location")

        # rectangle décoratif
        c.setStrokeColor(colors.grey)
        c.rect(1 * cm, height - 8.3 * cm, width - 2 * cm, 0.05 * cm, fill=1)

        # infos véhicule et période
        c.setFont("Helvetica", 10)
        c.drawString(2 * cm, height - 9 * cm, f"Véhicule: {vehicule.marque} {vehicule.modele} ({vehicule.annee})")

        # formatage dates
        date_debut = reservation.date_debut.strftime('%d/%m/%Y')
        date_fin = reservation.date_fin.strftime('%d/%m/%Y')
        c.drawString(2 * cm, height - 9.5 * cm, f"Période: du {date_debut} au {date_fin}")
        c.drawString(2 * cm, height - 10 * cm, f"Durée: {reservation.duree_en_jours()} jours")

    @staticmethod
    def _generer_tableau_montants(c, width, height, facture):
        """
        génère tableau des montants

        args:
            c: canvas reportlab
            width: largeur page
            height: hauteur page
            facture: objet facture
        """
        # titre section
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, height - 11.5 * cm, "Détails des montants")

        # rectangle décoratif
        c.setStrokeColor(colors.grey)
        c.rect(1 * cm, height - 11.8 * cm, width - 2 * cm, 0.05 * cm, fill=1)

        # calcul détails tva
        details_tva = {
            "taux_tva": facture.taux_tva * 100,  # en pourcentage
            "base_ht": facture.montant_ht,
            "montant_tva": facture.montant_ht * facture.taux_tva,
            "montant_ttc": facture.montant_ttc
        }

        # création tableau montants
        data = [
            ["Description", "Montant HT", "TVA", "Montant TTC"],
            ["Location de véhicule", f"{details_tva['base_ht']:.2f} €",
             f"{details_tva['montant_tva']:.2f} €", f"{details_tva['montant_ttc']:.2f} €"],
            ["", "", "Total", f"{details_tva['montant_ttc']:.2f} €"]
        ]

        # style tableau
        tableau = Table(data, colWidths=[8 * cm, 3 * cm, 3 * cm, 3 * cm])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -2), 0.25, colors.black),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
            ('GRID', (-2, -1), (-1, -1), 0.25, colors.black),
        ])
        tableau.setStyle(style)

        # ajout tableau au document
        tableau.wrapOn(c, width - 4 * cm, height)
        tableau.drawOn(c, 2 * cm, height - 16 * cm)

    @staticmethod
    def _generer_pied_page(c, width, height):
        """
        génère pied de page

        args:
            c: canvas reportlab
            width: largeur page
            height: hauteur page
        """
        # rectangle décoratif
        c.setStrokeColor(colors.grey)
        c.rect(1 * cm, 3 * cm, width - 2 * cm, 0.05 * cm, fill=1)

        # texte pied de page
        c.setFont("Helvetica", 8)
        c.drawString(2 * cm, 2.5 * cm, "Merci de votre confiance.")
        c.drawString(2 * cm, 2 * cm, "Location de Véhicules - 123 rue des Voitures - 75000 Paris")
        c.drawString(2 * cm, 1.5 * cm, "SIRET: 123 456 789 00012 - TVA: FR12 123 456 789")

        # numéro page
        c.drawRightString(width - 2 * cm, 1 * cm, "Page 1/1")


# exemple utilisation (exécution uniquement si fichier lancé directement)
if __name__ == "__main__":
    # import pour exemple
    from datetime import datetime, timedelta


    # création objets fictifs pour test
    class FactureTest:
        def __init__(self):
            self.id = 1
            self.reservation_id = 101
            self.date_emission = datetime.now()
            self.montant_ht = 250.0
            self.taux_tva = 0.2
            self.montant_ttc = 300.0


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
            return 6  # exemple simplifié


    # création objets test
    facture = FactureTest()
    client = ClientTest()
    vehicule = VehiculeTest()
    reservation = ReservationTest()

    # génération pdf
    chemin_pdf = PDFGenerator.generer_facture(facture, client, vehicule, reservation)
    print(f"PDF généré avec succès: {chemin_pdf}")