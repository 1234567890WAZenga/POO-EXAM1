# decorators/class_decorators.py
"""
Décorateur de classe : ajoute un suivi automatique des performances
sans modifier la logique métier.

But pédagogique :
- cross-cutting concern
- enrichissement transparent d'une classe existante
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Callable


def add_performance_tracking(cls):
    """
    Décorateur de classe.

    Il wrappe une méthode cible :
    - prioritaire: send_notification()
    - sinon: send()

    Il mesure le temps d'exécution et stocke des métriques sur la classe/instance.
    """

    # Déterminer la méthode à wrapper
    target_name = None
    if hasattr(cls, "send_notification") and callable(getattr(cls, "send_notification")):
        target_name = "send_notification"
    elif hasattr(cls, "send") and callable(getattr(cls, "send")):
        target_name = "send"

    if target_name is None:
        raise TypeError(
            f"{cls.__name__} doit définir send_notification() ou send() pour activer add_performance_tracking."
        )

    original: Callable[..., Any] = getattr(cls, target_name)

    # Espace métriques (par classe)
    if not hasattr(cls, "_perf_stats"):
        cls._perf_stats = {
            "count": 0,
            "total_ms": 0.0,
            "min_ms": None,
            "max_ms": None,
            "last_ms": None,
        }

    def tracked(self, *args, **kwargs):
        start = time.perf_counter()
        try:
            return original(self, *args, **kwargs)
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000.0

            stats = cls._perf_stats
            stats["count"] += 1
            stats["total_ms"] += elapsed_ms
            stats["last_ms"] = elapsed_ms

            if stats["min_ms"] is None or elapsed_ms < stats["min_ms"]:
                stats["min_ms"] = elapsed_ms
            if stats["max_ms"] is None or elapsed_ms > stats["max_ms"]:
                stats["max_ms"] = elapsed_ms

    # Remplacer la méthode par la version trackée
    setattr(cls, target_name, tracked)

    # Ajouter un getter de métriques (pratique pour la démo)
    def get_metrics(self) -> Dict[str, Any]:
        stats = cls._perf_stats
        avg = (stats["total_ms"] / stats["count"]) if stats["count"] else 0.0
        return {
            "method": target_name,
            "count": stats["count"],
            "avg_ms": avg,
            "min_ms": stats["min_ms"],
            "max_ms": stats["max_ms"],
            "last_ms": stats["last_ms"],
        }

    setattr(cls, "get_metrics", get_metrics)

    return cls
