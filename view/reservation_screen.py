from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDateEdit, QPushButton, QTableWidget, \
    QTableWidgetItem, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate
from controller.parc_controller import ParcController
from controller.reservation_controller import ReservationController
from controller.client_controller import ClientController
from utils.database import Database
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QMessageBox,
    QTableWidgetItem,
    QHeaderView,
    QInputDialog,
    QAbstractItemView,
    QApplication
)
import re
from PyQt5.QtCore import QDate
from PyQt5.uic import loadUi


class ReservationScreen(QDialog):
    def __init__(self):
        super(ReservationScreen, self).__init__()
        loadUi('reservation.ui', self)

        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Initialisation de la base de données et des contrôleurs
        self.db = Database("../utils/test.db")
        self.parc_controller = ParcController(self.db)
        self.client_controller = ClientController(self.db)
        self.reservation_controller = ReservationController(self.db, self.parc_controller, self.client_controller)

        # Initialisation de l'interface
        self.typeBox.currentTextChanged.connect(self.on_type_change)
        self.searchButton.clicked.connect(self.rechercher)
        self.reserveButton.clicked.connect(self.reserver)
        # Connexion de la checkbox
        self.showUnavailableBox.stateChanged.connect(self.rechercher)

        # Configuration des dates par défaut
        self.startDate.setDate(QDate.currentDate())
        self.endDate.setDate(QDate.currentDate().addDays(1))

        # Chargement des types de véhicules
        self.load_types()

        # IMPORTANT: Connexions pour le calcul automatique du prix
        self.setup_date_connections()

    def load_types(self):
        """Charge les types de véhicules disponibles"""
        self.typeBox.addItems(["Voiture", "Utilitaire", "Moto"])
        self.on_type_change("Voiture")

    def on_type_change(self, type_selected):
        """Met à jour les critères selon le type de véhicule sélectionné"""
        self.criteriaBox.clear()
        if type_selected == "Voiture":
            self.criteriaBox.addItems(["Puissance > 100", "Essence", "Diesel"])
        elif type_selected == "Utilitaire":
            self.criteriaBox.addItems(["Volume > 9 m³"])
        elif type_selected == "Moto":
            self.criteriaBox.addItems(["Cylindrée > 500"])

    def rechercher(self):
        """Recherche les véhicules disponibles selon les critères"""
        try:
            # Récupération des paramètres de recherche
            type_vehicule = self.typeBox.currentText()
            date_debut = self.startDate.date().toPyDate()
            date_fin = self.endDate.date().toPyDate()
            critere_selectionne = self.criteriaBox.currentText()

            # Conversion des dates Python en datetime
            datetime_debut = datetime.combine(date_debut, datetime.min.time())
            datetime_fin = datetime.combine(date_fin, datetime.min.time())

            # Construction des critères selon le type et la sélection
            criteres = {}
            if type_vehicule == "Voiture" and "Puissance" in critere_selectionne:
                criteres = {"puissance": {"min": 100}}
            elif type_vehicule == "Voiture" and critere_selectionne in ["Essence", "Diesel"]:
                criteres = {"carburant": critere_selectionne}
            elif type_vehicule == "Utilitaire" and "Volume" in critere_selectionne:
                criteres = {"volume": {"min": 9}}
            elif type_vehicule == "Moto" and "Cylindrée" in critere_selectionne:
                criteres = {"cylindree": {"min": 500}}

            # DEBUG: Avant la recherche de disponibilité
            # print(f"DEBUG: Recherche pour véhicule type {type_vehicule}, dates {datetime_debut} à {datetime_fin}")
            # print(f"DEBUG: Nombre total de réservations dans le parc: {len(self.parc_controller.parc.reservations)}")

            # Filtrage selon la checkbox
            if self.showUnavailableBox.isChecked():
                # Afficher tous les véhicules (disponibles + indisponibles)
                # print("DEBUG: Affichage de tous les véhicules (disponibles + indisponibles)")
                tous_vehicules = self.parc_controller.rechercher_vehicules(criteres={"type": type_vehicule})
                vehicules_a_afficher = []
                for v in tous_vehicules:
                    if self._correspond_criteres(v, criteres):
                        vehicules_a_afficher.append(v)
            else:
                # Afficher seulement les disponibles (comportement actuel)
                # print("DEBUG: Affichage seulement des véhicules disponibles")
                vehicules_a_afficher = self.parc_controller.verifier_disponibilite(
                    type_vehicule, criteres, datetime_debut, datetime_fin
                )

            if not vehicules_a_afficher:
                QMessageBox.information(self, "Aucun résultat", "Aucun véhicule trouvé pour ces critères.")
                self._clear_table()
                return

            # Affichage des résultats
            self._afficher_vehicules(vehicules_a_afficher, type_vehicule)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche : {str(e)}")
            self._clear_table()

    def setup_date_connections(self):
        """Connecte les changements de dates au recalcul du prix"""
        if hasattr(self, 'startDate'):
            self.startDate.dateChanged.connect(self.on_dates_changed)
        if hasattr(self, 'endDate'):
            self.endDate.dateChanged.connect(self.on_dates_changed)
        if hasattr(self, 'typeBox'):
            self.typeBox.currentTextChanged.connect(self.on_dates_changed)

    def on_dates_changed(self):
        """Appelée quand les dates changent"""
        if (hasattr(self, 'tableWidget') and
                self.tableWidget.currentRow() >= 0 and
                hasattr(self, 'startDate') and
                hasattr(self, 'endDate')):
            self.calculer_et_afficher_devis()

    def calculer_et_afficher_devis(self):
        """Calcule et affiche le prix du véhicule sélectionné"""
        try:
            # Vérifier qu'un véhicule est sélectionné dans le tableau
            current_row = self.tableWidget.currentRow()
            if current_row < 0:
                return

            # Récupérer l'ID du véhicule depuis le tableau
            vehicule_id = int(self.tableWidget.item(current_row, 0).text())

            # Récupérer les dates depuis vos champs
            date_debut = self.startDate.date().toPyDate()
            date_fin = self.endDate.date().toPyDate()

            if date_fin <= date_debut:
                self._afficher_message_prix("❌ La date de fin doit être après la date de début", "red")
                return

            # Appel au contrôleur pour obtenir le devis
            devis = self.reservation_controller.obtenir_devis(vehicule_id, date_debut, date_fin)

            if devis:
                # Affichage du calcul de prix
                texte_devis = f"""📊 DEVIS DÉTAILLÉ:

⏱️ Durée: {devis['nb_jours']} jour(s)
💰 Tarif journalier: {devis['tarif_journalier']:.2f}€
📝 Prix de base: {devis['prix_base']:.2f}€"""

                if devis['reduction_pourcent'] > 0:
                    texte_devis += f"""
🎉 Réduction ({devis['reduction_pourcent']}%): -{devis['economie']:.2f}€"""

                texte_devis += f"""

💳 PRIX TOTAL: {devis['prix_final']:.2f}€"""

                self._afficher_message_prix(texte_devis, "green")
            else:
                self._afficher_message_prix("❌ Erreur de calcul du prix", "red")

        except Exception as e:
            self._afficher_message_prix(f"❌ Erreur: {str(e)}", "red")
            print(f"Erreur calcul devis: {e}")

    def _correspond_criteres(self, vehicule, criteres):
        """Vérifie si un véhicule correspond aux critères (copie de la logique du parc)"""
        if not criteres:
            return True

        for cle, valeur in criteres.items():
            if not hasattr(vehicule, cle):
                return False
            attr_valeur = getattr(vehicule, cle)

            if isinstance(valeur, dict):
                if "min" in valeur and attr_valeur < valeur["min"]:
                    return False
                if "max" in valeur and attr_valeur > valeur["max"]:
                    return False
            elif isinstance(attr_valeur, list) and isinstance(valeur, str):
                if valeur not in attr_valeur:
                    return False
            elif attr_valeur != valeur:
                return False

        return True

    def _afficher_message_prix(self, message, couleur):
        """Affiche le message de prix"""
        # Option 1: Si vous avez un label dans votre .ui
        if hasattr(self, 'labelPrix'):
            self.labelPrix.setText(message)
            if couleur == "green":
                self.labelPrix.setStyleSheet(
                    "color: green; border: 1px solid green; padding: 5px; background-color: #f0fff0;")
            else:
                self.labelPrix.setStyleSheet(
                    "color: red; border: 1px solid red; padding: 5px; background-color: #fff0f0;")

        # Option 2: Affichage dans la console (toujours actif)
        print(f"PRIX: {message}")

    def _afficher_vehicules(self, vehicules, type_vehicule):
        """Affiche les véhicules dans le tableau"""
        # Détermination des colonnes selon le type de véhicule
        if type_vehicule == "Voiture":
            colonnes = ["ID", "Marque", "Modèle", "Année", "Carburant", "Puissance", "Places", "Disponible"]
            attributs = ["id", "marque", "modele", "annee", "carburant", "puissance", "nb_places", "disponible"]
        elif type_vehicule == "Utilitaire":
            colonnes = ["ID", "Marque", "Modèle", "Année", "Volume", "Charge utile", "Hayon", "Disponible"]
            attributs = ["id", "marque", "modele", "annee", "volume", "charge_utile", "hayon", "disponible"]
        elif type_vehicule == "Moto":
            colonnes = ["ID", "Marque", "Modèle", "Année", "Cylindrée", "Type", "Disponible"]
            attributs = ["id", "marque", "modele", "annee", "cylindree", "type", "disponible"]

        # Configuration du tableau
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(len(colonnes))
        self.tableWidget.setHorizontalHeaderLabels(colonnes)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)

        # Récupération des dates pour vérifier disponibilité
        date_debut = self.startDate.date().toPyDate()
        date_fin = self.endDate.date().toPyDate()
        datetime_debut = datetime.combine(date_debut, datetime.min.time())
        datetime_fin = datetime.combine(date_fin, datetime.min.time())

        # Ajout des véhicules au tableau
        for vehicule in vehicules:
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)

            for col, attribut in enumerate(attributs):
                if attribut == "disponible":
                    # Vérification de disponibilité
                    disponible = self.parc_controller.verifier_disponibilite_vehicule(
                        vehicule.id, datetime_debut, datetime_fin
                    )
                    statut = "✅ Disponible" if disponible else "❌ Occupée"
                    item = QTableWidgetItem(statut)
                elif attribut:
                    valeur = getattr(vehicule, attribut, "")
                    if attribut == "hayon":
                        valeur = "Oui" if valeur else "Non"
                    item = QTableWidgetItem(str(valeur))
                else:
                    item = QTableWidgetItem("")

                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.tableWidget.setItem(row, col, item)

    def _clear_table(self):
        """Vide le tableau"""
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)

    def reserver(self):
        """Créer une réservation pour le véhicule sélectionné"""
        try:
            # Vérifier qu'un véhicule est sélectionné
            current_row = self.tableWidget.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner un véhicule à réserver")
                return

            # Récupérer l'ID du véhicule depuis le tableau
            vehicule_id = int(self.tableWidget.item(current_row, 0).text())

            # Récupérer les informations du véhicule pour l'affichage
            marque = self.tableWidget.item(current_row, 1).text()
            modele = self.tableWidget.item(current_row, 2).text()
            annee = self.tableWidget.item(current_row, 3).text()
            vehicule_info = f"{marque} {modele} ({annee})"

            # Récupérer les dates
            date_debut = self.startDate.date().toPyDate()
            date_fin = self.endDate.date().toPyDate()

            # Conversion en datetime
            datetime_debut = datetime.combine(date_debut, datetime.min.time())
            datetime_fin = datetime.combine(date_fin, datetime.min.time())

            # Validation des dates
            if datetime_debut >= datetime_fin:
                QMessageBox.warning(self, "Dates invalides", "La date de fin doit être postérieure à la date de début")
                return

            # NOUVEAU: Calculer le devis avant de continuer
            devis = self.reservation_controller.obtenir_devis(vehicule_id, date_debut, date_fin)
            prix_info = ""
            if devis:
                prix_info = f"\n💰 Prix calculé: {devis['prix_final']:.2f}€ pour {devis['nb_jours']} jour(s)"
                if devis['reduction_pourcent'] > 0:
                    prix_info += f" (réduction de {devis['reduction_pourcent']}%)"

            # Sélection du client
            try:
                clients_disponibles = self.client_controller.lister_tous_clients() if hasattr(self,
                                                                                              'client_controller') and self.client_controller else []

                if not clients_disponibles:
                    client_id, ok = QInputDialog.getInt(
                        self,
                        "Client",
                        f"Aucun client trouvé en base.\nEntrez manuellement l'ID du client:{prix_info}",
                        value=1,
                        min=1,
                        max=9999
                    )
                    if not ok:
                        return
                else:
                    items_clients = []
                    for client in clients_disponibles:
                        item_text = f"{client.prenom} {client.nom} (ID: {client.id})"
                        items_clients.append(item_text)

                    client_choisi, ok = QInputDialog.getItem(
                        self,
                        "Sélection du client",
                        f"Choisissez le client pour cette réservation:{prix_info}",
                        items_clients,
                        0,
                        False
                    )

                    if not ok:
                        return

                    match = re.search(r'\(ID: (\d+)\)', client_choisi)
                    if match:
                        client_id = int(match.group(1))
                    else:
                        QMessageBox.warning(self, "Erreur", "Impossible d'extraire l'ID du client")
                        return

            except Exception as e:
                # print(f"DEBUG: Erreur lors de la récupération des clients: {e}")
                client_id, ok = QInputDialog.getInt(
                    self,
                    "Client",
                    f"Erreur de récupération des clients ({e}).\nEntrez manuellement l'ID:{prix_info}",
                    value=1,
                    min=1,
                    max=9999
                )
                if not ok:
                    return

            # Création de la réservation avec prix calculé automatiquement
            # print(f"DEBUG: Création de réservation avec prix automatique")
            resultat = self.reservation_controller.creer_reservation(
                client_id, vehicule_id, datetime_debut, datetime_fin
            )

            reservation = resultat['reservation']
            facture_pdf = resultat.get('facture_pdf', None)

            if reservation:
                # Message avec prix détaillé
                message = f"✅ Réservation confirmée !\n\n"
                message += f"📋 Numéro: {reservation.id}\n"
                message += f"👤 Client ID: {client_id}\n"
                message += f"🚗 Véhicule: {vehicule_info}\n"
                message += f"📅 Du {datetime_debut.strftime('%d/%m/%Y')} au {datetime_fin.strftime('%d/%m/%Y')}\n"

                # Affichage du prix calculé
                if hasattr(reservation, 'prix_total') and reservation.prix_total:
                    duree = (datetime_fin.date() - datetime_debut.date()).days
                    message += f"⏱️ Durée: {duree} jour(s)\n"
                    message += f"💰 Prix total: {reservation.prix_total:.2f}€\n"

                if facture_pdf:
                    message += f"\n✓ Facture PDF: {facture_pdf}"

                QMessageBox.information(self, "Réservation confirmée", message)
                self.rechercher()  # Actualiser l'affichage
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de créer la réservation")

        except ValueError as e:
            QMessageBox.critical(self, "Erreur de saisie", f"Données invalides: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la réservation: {str(e)}")
            # print(f"DEBUG: Erreur détaillée - {e}")
            import traceback
            traceback.print_exc()