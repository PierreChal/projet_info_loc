"""
générateur de factures en pdf
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors


class PDFGenerator:
    """classe pour générer des factures au format pdf"""

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
        # Ajout du logo
        try:
            # Chercher le logo dans plusieurs emplacements possibles
            possible_paths = [
                os.path.join('utils', 'assets', 'logo.png'),
                os.path.join('assets', 'logo.png'),
                'logo.png',
                os.path.join('..', 'assets', 'logo.png'),
                os.path.join(os.path.dirname(__file__), 'assets', 'logo.png'),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils', 'assets', 'logo.png')
            ]

            logo_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    logo_path = path
                    break

            if logo_path:
                # Dimensions du logo
                logo_width = 4 * cm
                logo_height = 2 * cm
                # Position du logo en haut à gauche
                c.drawImage(logo_path, 1 * cm, height - 3 * cm,
                           width=logo_width, height=logo_height,
                           preserveAspectRatio=True)
                print(f"✓ Logo ajouté depuis {logo_path}")
            else:
                print(f"⚠ Logo non trouvé. Chemins testés:")
                for path in possible_paths:
                    print(f"  - {path} (existe: {os.path.exists(path)})")

        except Exception as e:
            print(f"✗ Erreur lors du chargement du logo: {e}")

        # En-tête avec nom entreprise (décalé vers la droite pour le logo)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(6 * cm, height - 2 * cm, "RouleMaPoulette")

        # Infos facture
        c.setFont("Helvetica-Bold", 14)
        c.drawString(width - 6 * cm, height - 2 * cm, "FACTURE")

        c.setFont("Helvetica", 10)
        c.drawString(width - 6 * cm, height - 2.5 * cm, f"N° {facture.id}")
        c.drawString(width - 6 * cm, height - 3 * cm, f"Date: {facture.date_emission.strftime('%d/%m/%Y')}")

        # Rectangle décoratif
        c.setStrokeColor(colors.grey)
        c.rect(1 * cm, height - 3.5 * cm, width - 2 * cm, 0.1 * cm, fill=1)

        # Infos client
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
        génère la section détails de la location

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

        # ligne de séparation
        c.setStrokeColor(colors.grey)
        c.line(2 * cm, height - 8.5 * cm, width - 2 * cm, height - 8.5 * cm)

        # détails véhicule
        c.setFont("Helvetica", 10)
        c.drawString(2 * cm, height - 9.2 * cm, f"Véhicule: {vehicule.marque} {vehicule.modele} ({vehicule.annee})")
        c.drawString(2 * cm, height - 9.7 * cm, f"Réservation N°: {reservation.id}")
        c.drawString(2 * cm, height - 10.2 * cm, f"Période: du {reservation.date_debut.strftime('%d/%m/%Y')} au {reservation.date_fin.strftime('%d/%m/%Y')}")
        c.drawString(2 * cm, height - 10.7 * cm, f"Durée: {reservation.duree_en_jours()} jour(s)")

    @staticmethod
    def _generer_tableau_montants(c, width, height, facture):
        """
        génère le tableau des montants

        args:
            c: canvas reportlab
            width: largeur page
            height: hauteur page
            facture: objet facture
        """
        # calcul détails tva
        details_tva = facture.calculer_details_tva()

        # position du tableau
        tableau_y = height - 13 * cm
        tableau_width = 8 * cm
        tableau_x = width - tableau_width - 2 * cm

        # en-tête tableau
        c.setFont("Helvetica-Bold", 12)
        c.drawString(tableau_x, tableau_y + 1 * cm, "Montants")

        # lignes du tableau
        c.setFont("Helvetica", 10)

        # montant ht
        c.drawString(tableau_x, tableau_y, "montant ht:")
        c.drawRightString(tableau_x + tableau_width, tableau_y, f"{details_tva['base_ht']:.2f} €")

        # tva
        c.drawString(tableau_x, tableau_y - 0.5 * cm, f"tva ({details_tva['taux_tva']:.1f}%):")
        c.drawRightString(tableau_x + tableau_width, tableau_y - 0.5 * cm, f"{details_tva['montant_tva']:.2f} €")

        # ligne de séparation
        c.setStrokeColor(colors.black)
        c.line(tableau_x, tableau_y - 0.8 * cm, tableau_x + tableau_width, tableau_y - 0.8 * cm)

        # total ttc
        c.setFont("Helvetica-Bold", 12)
        c.drawString(tableau_x, tableau_y - 1.2 * cm, "total ttc:")
        c.drawRightString(tableau_x + tableau_width, tableau_y - 1.2 * cm, f"{details_tva['montant_ttc']:.2f} €")

    @staticmethod
    def _generer_pied_page(c, width, height):
        """
        génère le pied de page

        args:
            c: canvas reportlab
            width: largeur page
            height: hauteur page
        """
        # informations de l'entreprise
        c.setFont("Helvetica", 8)
        pied_y = 3 * cm

        # Fonction helper pour centrer le texte
        def draw_centered_text(canvas, x, y, text):
            text_width = canvas.stringWidth(text, "Helvetica", 8)
            canvas.drawString(x - text_width / 2, y, text)

        draw_centered_text(c, width / 2, pied_y,
                         "roulemapoulette - location de véhicules")
        draw_centered_text(c, width / 2, pied_y - 0.4 * cm,
                         "123 avenue de la location, 75000 paris")
        draw_centered_text(c, width / 2, pied_y - 0.8 * cm,
                         "tél: 01 23 45 67 89 | email: contact@roulemapoulette.fr")
        draw_centered_text(c, width / 2, pied_y - 1.2 * cm,
                         "siret: 123 456 789 00012 | tva intracommunautaire: fr12345678901")

    @staticmethod
    @staticmethod
    def generer_facture(facture, client, vehicule, reservation, chemin_sortie=None):
        """Génère une facture PDF"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from datetime import datetime

            # SIMPLE: Utiliser le chemin fourni ou nom par défaut
            if chemin_sortie:
                nom_fichier = chemin_sortie
            else:
                nom_fichier = f"facture_{facture.id}.pdf"

            # Création du PDF (votre code existant)
            c = canvas.Canvas(nom_fichier, pagesize=A4)
            width, height = A4

            # Votre code PDF existant ici...
            # (En-tête, client, véhicule, prix, etc.)

            c.save()
            return nom_fichier

        except Exception as e:
            print(f"Erreur PDF: {e}")
            raise e


# Code de test
if __name__ == "__main__":
    from datetime import datetime, timedelta
    import sys
    import os

    print("=== Test de génération de facture PDF ===")
    print(f"Répertoire de travail: {os.getcwd()}")
    print(f"Fichier exécuté: {__file__}")
    print(f"Répertoire du fichier: {os.path.dirname(__file__)}")

    # Vérification des chemins possibles pour le logo
    print("\n=== Vérification des chemins pour le logo ===")
    possible_paths = [
        os.path.join('utils', 'assets', 'logo.png'),
        os.path.join('assets', 'logo.png'),
        'logo.png',
        os.path.join('..', 'assets', 'logo.png'),
        os.path.join(os.path.dirname(__file__), 'assets', 'logo.png'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils', 'assets', 'logo.png')
    ]

    for path in possible_paths:
        exists = os.path.exists(path)
        print(f"  {path}: {'✓' if exists else '✗'}")

    # Classes de test simplifiées
    class FactureTest:
        def __init__(self):
            self.id = 1001
            self.reservation_id = 2001
            self.date_emission = datetime.now()
            self.montant_ht = 250.0
            self.taux_tva = 0.2
            self.montant_ttc = 300.0

        def calculer_details_tva(self):
            return {
                "taux_tva": self.taux_tva * 100,
                "base_ht": self.montant_ht,
                "montant_tva": self.montant_ht * self.taux_tva,
                "montant_ttc": self.montant_ttc
            }

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
            self.id = 2001
            self.date_debut = datetime.now()
            self.date_fin = datetime.now() + timedelta(days=5)

        def duree_en_jours(self):
            return 5

    # Création des objets de test
    print("\n=== Création des données de test ===")
    facture = FactureTest()
    client = ClientTest()
    vehicule = VehiculeTest()
    reservation = ReservationTest()

    # Génération de la facture
    print("\n=== Génération de la facture ===")
    try:
        chemin_pdf = PDFGenerator.generer_facture(facture, client, vehicule, reservation)
        print(f"✓ Facture générée avec succès: {chemin_pdf}")

        # Vérification du fichier
        if os.path.exists(chemin_pdf):
            taille = os.path.getsize(chemin_pdf)
            print(f"✓ Fichier créé: {taille} octets")
        else:
            print("✗ Erreur: Fichier non créé")

    except Exception as e:
        print(f"✗ Erreur lors de la génération: {e}")
        import traceback
        traceback.print_exc()