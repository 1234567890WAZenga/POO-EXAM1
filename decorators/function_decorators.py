# decorators/function_decorators.py
"""
Décorateurs de fonctions (POO avancée).

Objectifs :
- démontrer les décorateurs avec *args/**kwargs
- ajouter du logging transversal
- ajouter un retry paramétrable (résilience)

Remarque :
- Ce module doit rester générique (pas dépendant d'un contexte précis).
- Il supporte des priorités passées en str/int/Enum (ex: core.models.Priority).
"""

import functools
import time
from typing import Any, Callable, Optional

try:
    # Optionnel : si core.models.Priority existe, on peut reconnaître ses valeurs
    from core.models import Priority  # type: ignore
except Exception:
    Priority = None  # type: ignore


def log_notification(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Log simple : journalise le nom de la fonction + args/kwargs.
    Compatible avec toute signature grâce à *args/**kwargs.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] {func.__name__} called args={args} kwargs={kwargs}")
        return func(*args, **kwargs)
    return wrapper


def _is_urgent_priority(value: Any) -> bool:
    """
    Détermine si la priorité correspond à URGENT.

    Accepte :
    - Enum Priority (IntEnum)
    - str : "URGENT"
    - int : 4 (si mapping LOW=1..URGENT=4)
    """
    # Priority Enum (si disponible)
    if Priority is not None and isinstance(value, Priority):
        return int(value.value) == 4

    # str
    if isinstance(value, str):
        return value.strip().upper() == "URGENT"

    # int
    if isinstance(value, int):
        return value == 4

    return False


def retry_on_failure(max_retries: int = 3, delay_seconds: float = 0.0, urgent_bonus: int = 0) -> Callable:
    """
    Décorateur paramétrable de retry.

    - max_retries : nombre de tentatives
    - delay_seconds : délai entre tentatives
    - urgent_bonus : tentatives supplémentaires si la priorité est "URGENT"
      (optionnel, utile pour démonstration)

    Le wrapper accepte *args/**kwargs pour être générique.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = max_retries

            # Bonus si on reçoit une priorité urgente en kwargs (ex: priority=Priority.URGENT)
            if urgent_bonus > 0 and "priority" in kwargs and _is_urgent_priority(kwargs["priority"]):
                retries += urgent_bonus

            last_exc: Optional[Exception] = None

            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    print(f"[RETRY] {func.__name__} attempt {attempt}/{retries} failed: {exc}")
                    if delay_seconds > 0 and attempt < retries:
                        time.sleep(delay_seconds)

            # Après tous les essais, on relance l'exception finale
            raise last_exc  # type: ignore

        return wrapper
    return decorator
