 
# core/registry.py
"""
Registry global des notificateurs.

Rôle :
- conserver toutes les classes de notificateurs enregistrées automatiquement
- permettre au dispatcher / à la démo de lister et récupérer un notificateur par nom/type
"""

from __future__ import annotations

from typing import Dict, Type, Optional, List, Any


class NotificationRegistry:
    """
    Registre global in-memory (simple et suffisant pour la phase POO).
    """

    # Stockage interne: { "classname": ClassRef }
    _registry: Dict[str, Type[Any]] = {}

    @classmethod
    def register(cls, name: str, notifier_cls: Type[Any]) -> None:
        """
        Enregistre une classe de notificateur dans le registre.

        - name: clé d'enregistrement (souvent le nom de classe)
        - notifier_cls: la classe (pas une instance)
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Registry.register: name doit être une chaîne non vide.")
        if notifier_cls is None:
            raise ValueError("Registry.register: notifier_cls ne peut pas être None.")

        cls._registry[name] = notifier_cls

    @classmethod
    def get(cls, name: str) -> Optional[Type[Any]]:
        """
        Récupère une classe enregistrée par son nom.
        Retourne None si absent.
        """
        return cls._registry.get(name)

    @classmethod
    def all(cls) -> List[Type[Any]]:
        """Retourne la liste des classes enregistrées."""
        return list(cls._registry.values())

    @classmethod
    def names(cls) -> List[str]:
        """Retourne la liste des noms de classes enregistrées."""
        return list(cls._registry.keys())

    @classmethod
    def clear(cls) -> None:
        """Vide le registre (utile en tests)."""
        cls._registry.clear()
