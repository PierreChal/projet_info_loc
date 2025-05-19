# utils/pdf_generator.py
# utilitaires pour la génération de documents pdf

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
        # Ajout du logo - avec une recherche plus robuste du chemin
        try:
            # Liste des chemins possibles à essayer pour trouver le logo
            possible_paths = [
                os.path.join('utils', 'assets', 'logo.png'),  # Chemin initial
                os.path.join('..', 'utils', 'assets', 'logo.png'),  # Un niveau au-dessus
                os.path.abspath(os.path.join('utils', 'assets', 'logo.png')),  # Chemin absolu
                # Chemin basé sur l'emplacement du script actuel
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo.png'),
                # Si pdf_generator.py est lui-même dans utils
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'utils', 'assets', 'logo.png'),
            ]

            # Essayer chaque chemin possible
            logo_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    logo_path = path
                    print(f"Logo trouvé à: {logo_path}")
                    break

            if logo_path:
                # Dimensions du logo (ajustez selon votre logo)
                logo_width = 5 * cm
                logo_height = 2 * cm
                # Position du logo en haut à gauche
                c.drawImage(logo_path, 1 * cm, height - 3 * cm, width=logo_width, height=logo_height,
                            preserveAspectRatio=True)
            else:
                print(f"Logo non trouvé. Chemins essayés: {possible_paths}")
        except Exception as e:
            print(f"Erreur lors du chargement du logo: {e}")
            # Si erreur, on continue sans logo

        # en-tête avec nom entreprise (décalé vers la droite pour laisser place au logo)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(7 * cm, height - 2 * cm, "Location de Véhicules")

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
        # Ajout du logo (depuis le fichier utils/assets/logo.png)
        try:
            # Chemin vers le logo
            logo_path = os.path.join('utils', 'assets', 'logo.png')
            # Vérifier si le fichier existe
            if os.path.exists(logo_path):
                # Dimensions du logo (ajustez selon votre logo)
                logo_width = 5 * cm
                logo_height = 2 * cm
                # Position du logo en haut à gauche
                c.drawImage(logo_path, 1 * cm, height - 3 * cm, width=logo_width, height=logo_height,
                            preserveAspectRatio=True)
            else:
                print(f"Logo non trouvé: {logo_path}")
        except Exception as e:
            print(f"Erreur lors du chargement du logo: {e}")
            # Si erreur, on continue sans logo

        # en-tête avec nom entreprise (décalé vers la droite pour laisser place au logo)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(7 * cm, height - 2 * cm, "Location de Véhicules")

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
    import os
    import sys

    # Vérifier que le dossier pour le logo existe, sinon le créer
    assets_dir = os.path.join('utils', 'assets')
    if not os.path.exists(assets_dir):
        print(f"Création du dossier {assets_dir} pour le logo...")
        try:
            os.makedirs(assets_dir)
            print(f"✓ Dossier {assets_dir} créé avec succès.")
        except Exception as e:
            print(f"✗ Erreur lors de la création du dossier: {e}")
            sys.exit(1)

    # Vérifier que le logo existe, sinon créer un logo de test
    logo_path = os.path.join(assets_dir, 'logo.png')
    if not os.path.exists(logo_path):
        print(f"Logo non trouvé à {logo_path}, création d'un logo de test...")
        try:
            # Essayer d'utiliser PIL pour créer une image simple
            try:
                from PIL import Image

                # Créer une image rouge simple de 200x100 pixels
                img = Image.new('RGB', (200, 100), color='red')
                img.save(logo_path)
                print(f"✓ Logo de test créé avec PIL à {logo_path}")
            except ImportError:
                # Si PIL n'est pas disponible, créer un fichier PNG minimal
                # Format PNG minimal (en-tête + IHDR + IEND)
                png_header = b'\x89PNG\r\n\x1a\n'
                ihdr_chunk = b'\x00\x00\x00\r' + b'IHDR' + b'\x00\x00\x00d' + b'\x00\x00\x00d' + b'\x08\x02\x00\x00\x00' + b'\xbf\x12\x8a\x1d'
                iend_chunk = b'\x00\x00\x00\x00' + b'IEND' + b'\xaeB`\x82'

                with open(logo_path, 'wb') as f:
                    f.write(png_header + ihdr_chunk + iend_chunk)
                print(f"✓ Logo de test créé manuellement à {logo_path}")
        except Exception as e:
            print(f"✗ Erreur lors de la création du logo de test: {e}")
            print("La génération du PDF continuera mais le logo pourrait ne pas apparaître.")


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


    print("\nPréparation des données pour la génération de facture...")
    # création objets test
    facture = FactureTest()
    client = ClientTest()
    vehicule = VehiculeTest()
    reservation = ReservationTest()

    print("\nGénération de la facture PDF avec logo...")
    try:
        # génération pdf
        chemin_pdf = PDFGenerator.generer_facture(facture, client, vehicule, reservation)

        # Vérifier que le fichier a bien été créé
        if os.path.exists(chemin_pdf):
            taille = os.path.getsize(chemin_pdf)
            print(f"✓ PDF généré avec succès: {chemin_pdf} ({taille} octets)")

            # Vérification supplémentaire - tenter de détecter si le logo a été intégré
            try:
                from PyPDF2 import PdfReader

                reader = PdfReader(chemin_pdf)
                page = reader.pages[0]

                # Essayer de détecter des objets image
                resources = page.get('/Resources', {})
                xobjects = resources.get('/XObject', {})
                if len(xobjects) > 0:
                    print("✓ Le PDF contient des images (le logo est probablement inclus)")
                else:
                    print("⚠ Aucune image détectée dans le PDF, le logo pourrait ne pas avoir été inclus.")
            except Exception as e:
                print(f"ℹ Impossible de vérifier le contenu du PDF: {e}")
                print("  Pour confirmer visuellement, ouvrez le PDF généré.")
        else:
            print(f"✗ Erreur: Le fichier PDF n'a pas été créé à {chemin_pdf}")
    except Exception as e:
        print(f"✗ Erreur lors de la génération du PDF: {e}")