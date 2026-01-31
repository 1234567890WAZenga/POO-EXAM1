 
# descriptors/validators.py
"""
Descripteurs de validation.

Objectif :
- valider automatiquement les données à l'affectation (instance.attr = value)
- centraliser la validation (réutilisable dans User/Config/Notification)

On utilise un stockage par instance (id(instance)) pour rester simple en POO.
"""

from __future__ import annotations

import re
from typing import Dict, Optional, Any


class EmailDescriptor:
    """Valide un email à l'affectation."""

    EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

    def __init__(self, allow_none: bool = True):
        self.allow_none = allow_none
        self._values: Dict[int, Optional[str]] = {}

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self._values.get(id(instance))

    def __set__(self, instance, value: Optional[str]):
        # Autoriser None si configuré
        if value is None:
            if self.allow_none:
                self._values[id(instance)] = None
                return
            raise ValueError("Email obligatoire (None non autorisé).")

        if not isinstance(value, str):
            raise ValueError("Email doit être une chaîne.")

        if not self.EMAIL_RE.match(value):
            raise ValueError(f"Email invalide: {value}")

        self._values[id(instance)] = value


class PhoneDescriptor:
    """Valide un numéro de téléphone simple (8 à 15 chiffres, option '+' au début)."""

    PHONE_RE = re.compile(r"^\+?[0-9]{8,15}$")

    def __init__(self, allow_none: bool = True):
        self.allow_none = allow_none
        self._values: Dict[int, Optional[str]] = {}

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self._values.get(id(instance))

    def __set__(self, instance, value: Optional[str]):
        if value is None:
            if self.allow_none:
                self._values[id(instance)] = None
                return
            raise ValueError("Phone obligatoire (None non autorisé).")

        if not isinstance(value, str):
            raise ValueError("Phone doit être une chaîne.")

        if not self.PHONE_RE.match(value):
            raise ValueError(f"Numéro invalide: {value}")

        self._values[id(instance)] = value


class PriorityDescriptor:
    """
    Valide la priorité.

    On accepte :
    - string parmi {"LOW","MEDIUM","HIGH","URGENT"} (case-insensitive)
    - int parmi {1..4} si vous voulez mapper plus tard
    """

    ALLOWED = {"LOW", "MEDIUM", "HIGH", "URGENT"}
    INT_MAP = {1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "URGENT"}

    def __init__(self, allow_none: bool = False):
        self.allow_none = allow_none
        self._values: Dict[int, Optional[str]] = {}

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self._values.get(id(instance))

    def __set__(self, instance, value: Any):
        if value is None:
            if self.allow_none:
                self._values[id(instance)] = None
                return
            raise ValueError("Priority obligatoire (None non autorisé).")

        # Autoriser int (1..4)
        if isinstance(value, int):
            if value not in self.INT_MAP:
                raise ValueError("Priority int doit être entre 1 et 4.")
            self._values[id(instance)] = self.INT_MAP[value]
            return

        # Autoriser str (LOW..URGENT)
        if isinstance(value, str):
            v = value.strip().upper()
            if v not in self.ALLOWED:
                raise ValueError(f"Priority invalide: {value}. Attendu: {sorted(self.ALLOWED)}")
            self._values[id(instance)] = v
            return

        raise ValueError("Priority doit être un str (LOW/MEDIUM/HIGH/URGENT) ou un int (1..4).")


# ------------------------------------------------------------
# Exemple d'objet de config utilisant les descripteurs
# (Vous pouvez le déplacer dans core/models.py plus tard)
# ------------------------------------------------------------

class NotificationConfig:
    """
    Exemple simple pour démontrer les descripteurs à l'oral.
    """
    email = EmailDescriptor(allow_none=True)
    phone = PhoneDescriptor(allow_none=True)
    priority = PriorityDescriptor(allow_none=False)

    def __init__(self, email: Optional[str], phone: Optional[str], priority: Any):
        # Déclenche automatiquement la validation via __set__
        self.email = email
        self.phone = phone
        self.priority = priority
