 # mixins/retry.py
"""
RetryMixin (résilience) + logique de fallback simple.

Objectif :
- ajouter un comportement transverse "retry" au niveau notifier
- coopératif avec super() (MRO)
- ne dépend pas encore du module decorators (Personne 2) pour éviter blocage.

Cible (déduit du focus technique) :
- Sécurité Campus : fiabilité, canaux redondants, confirmation.
"""

from __future__ import annotations

import time
from typing import Callable, List, Optional

from core.models import DeliveryResult, DeliveryStatus, Notification, User


class RetryMixin:
    """
    Mixin retry : encapsule une action et retente en cas d'échec logique.
    """
    max_retries: int = 3
    retry_delay_sec: float = 0.2

    def _retry(self, action: Callable[[], DeliveryResult]) -> DeliveryResult:
        last: Optional[DeliveryResult] = None

        for attempt in range(1, self.max_retries + 1):
            result = action()
            last = result

            if result.status != DeliveryStatus.FAILED:
                # Succès ou pending confirmation : on s'arrête
                return result

            # Échec => retry (si encore possible)
            self.log(f"Retry attempt {attempt}/{self.max_retries} failed: {result.error}")  # type: ignore[attr-defined]
            if attempt < self.max_retries:
                time.sleep(self.retry_delay_sec)

        # Après tous les essais, retourner le dernier échec
        return last  # type: ignore[return-value]


class FallbackMixin:
    """
    Mixin fallback : essaie les canaux dans l'ordre des préférences utilisateur.
    - utilise send_sms/send_email/send_push si disponibles (mixins de canaux)
    - la confirmation sera gérée au niveau dispatcher plus tard (Personne 4/2)
    """

    def send_with_fallback(self, notification: Notification, user: User) -> List[DeliveryResult]:
        results: List[DeliveryResult] = []

        # Respect opt-out sur type d'urgence
        if notification.emergency_type in user.preferences.opt_out_types:
            self.log(f"User opted-out for type={notification.emergency_type}")  # type: ignore[attr-defined]
            return results

        # Ordre préféré des canaux
        order = user.preferences.enabled_channels

        for ch_name in order:
            if ch_name == "sms" and hasattr(self, "send_sms"):
                res = self._retry(lambda: self.send_sms(notification, user))  # type: ignore[attr-defined]
                results.append(res)

            elif ch_name == "email" and hasattr(self, "send_email"):
                res = self._retry(lambda: self.send_email(notification, user))  # type: ignore[attr-defined]
                results.append(res)

            elif ch_name == "push" and hasattr(self, "send_push"):
                res = self._retry(lambda: self.send_push(notification, user))  # type: ignore[attr-defined]
                results.append(res)

            else:
                # canal inconnu ou pas mixin-injecté
                self.log(f"Channel '{ch_name}' not supported by notifier.")  # type: ignore[attr-defined]
                continue

            # Si un canal réussit (ou pending confirmation), on arrête le fallback
            if results[-1].status != DeliveryStatus.FAILED:
                break

        return results
