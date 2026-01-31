 
# core/metaclasses.py
"""
Métaclasse pour automatiser :
- l'ajout automatique d'une 'description' si absente
- la création d'une méthode validate_required_fields() si required_fields est défini
- l'enregistrement automatique dans NotificationRegistry

Idée clé :
La métaclasse intervient au moment de la création de la classe (pas à l'instanciation).
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List

from core.registry import NotificationRegistry


class NotificationMeta(type):
    """
    Métaclasse de notificateurs.
    """

    def __new__(mcls, name: str, bases: tuple, attrs: Dict[str, Any]):
        # 1) Ajouter une description par défaut si absente
        #    (utile à l'oral : "doc auto-générée")
        if "description" not in attrs:
            attrs["description"] = f"Notificateur de type {name}"

        # 2) Ajouter un type technique (clé stable) si absent
        #    (utile pour l'API plus tard)
        if "_notification_type" not in attrs:
            attrs["_notification_type"] = name.lower()

        # 3) Générer automatiquement un validateur si required_fields est présent
        required_fields = attrs.get("required_fields")
        if required_fields is not None and "validate_required_fields" not in attrs:
            attrs["validate_required_fields"] = mcls._create_required_fields_validator(required_fields)

        # 4) Créer la classe normalement
        klass = super().__new__(mcls, name, bases, attrs)

        # 5) Auto-enregistrement dans le registry
        #    On évite d'enregistrer les classes "abstraites" si un flag est présent.
        is_abstract = getattr(klass, "__abstract__", False)
        if not is_abstract:
            NotificationRegistry.register(name, klass)

        return klass

    @staticmethod
    def _create_required_fields_validator(required_fields: Iterable[str]) -> Callable[[Any, Dict[str, Any]], None]:
        """
        Génère une méthode validate_required_fields(self, payload) qui lève ValueError
        si payload ne contient pas tous les champs.
        """
        fields: List[str] = [str(f) for f in required_fields]

        def validate_required_fields(self, payload: Dict[str, Any]) -> None:
            if payload is None or not isinstance(payload, dict):
                raise ValueError("payload doit être un dict.")

            missing = [f for f in fields if f not in payload or payload.get(f) in (None, "")]
            if missing:
                raise ValueError(f"Champs obligatoires manquants: {missing}")

        return validate_required_fields
