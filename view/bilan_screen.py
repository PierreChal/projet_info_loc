from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from datetime import datetime

class BilanScreen(QDialog):
    def __init__(self, parc):
        super().__init__()
        self.parc = parc
        self.setWindowTitle("Bilan Comptable")
        self.setFixedSize(600, 400)

        self.layout = QVBoxLayout()
        self.revenus_label = QLabel()
        self.entretien_label = QLabel()
        self.rentabilite_label = QLabel()

        self.layout.addWidget(self.revenus_label)
        self.layout.addWidget(self.entretien_label)
        self.layout.addWidget(self.rentabilite_label)

        self.setLayout(self.layout)

        self.afficher_bilan()

    def afficher_bilan(self):
        # Revenus : toutes les réservations terminées ou confirmées
        revenus = sum(res.prix_total for res in self.parc.reservations
                      if res.statut in ["confirmée", "terminée"])

        # Coût d'entretien : total de tous les véhicules
        cout_entretien_total = sum(v.cout_entretien_annuel for v in self.parc.vehicules)

        # Rentabilité
        rentabilite = revenus - cout_entretien_total

        # Mise à jour des labels
        self.revenus_label.setText(f"💰 Revenus annuels : {revenus:.2f} €")
        self.entretien_label.setText(f"🛠️ Coût d’entretien annuel : {cout_entretien_total:.2f} €")
        self.rentabilite_label.setText(f"📈 Rentabilité : {rentabilite:.2f} €")

        if rentabilite < 0:
            self.rentabilite_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.rentabilite_label.setStyleSheet("color: green; font-weight: bold;")
