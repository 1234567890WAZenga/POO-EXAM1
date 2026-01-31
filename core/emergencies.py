 
# core/emergencies.py
"""
Types d'urgence (4+).

Cible de groupe (déduit du focus technique) :
- Sécurité Campus : priorité forte, canaux redondants, confirmation.

Note :
Le document du cours propose plusieurs spécialisations. Ici on prépare un noyau
générique qui marche pour toutes, mais optimisé pour un contexte "Sécurité Campus".
"""

from __future__ import annotations

from enum import Enum


class EmergencyType(str, Enum):
    SECURITY = "security"               # Alerte sécurité (intrusion, violence, etc.)
    WEATHER = "weather"                 # Météo extrême (orage, inondation, etc.)
    HEALTH = "health"                   # Santé (épidémie, urgence médicale)
    INFRASTRUCTURE = "infrastructure"   # Panne électrique, incendie, réseau, etc.
    ACADEMIC = "academic"               # Information académique (optionnel mais utile)
    OTHER = "other"                     # Autre type d'urgence