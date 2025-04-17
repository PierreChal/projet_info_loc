"""
Package contenant les design patterns utilisés dans le système de réservation de véhicules.
"""

from patterns.composite import ComposantParcVehicules, VehiculeComposant
from patterns.parc_vehicules import ParcVehicules

__all__ = ['ComposantParcVehicules', 'VehiculeComposant', 'ParcVehicules']