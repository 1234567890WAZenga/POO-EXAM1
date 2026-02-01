"""
mixins/retry.py

Retry + fallback (simulation) pour la démo.
- RetryMixin : re-tente un même canal N fois en cas d'exception.
- FallbackMixin : essaye les canaux dans un ordre (sms -> email -> push)
  en respectant les préférences de l'utilisateur.
"""

from __future__ import annotations

from typing import Callable, List

from core.models import DeliveryResult, DeliveryStatus, Notification, User


class RetryMixin:
    """
    Retry coopératif.
    Utilisé quand un canal lève une exception (échec temporaire).
    """
    max_retries = 2

    def run_with_retry(self, fn: Callable[[], DeliveryResult]) -> DeliveryResult:
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                return fn()
            except Exception as e:
                last_error = str(e)
                self.log(f"Retry attempt {attempt}/{self.max_retries} failed: {last_error}")

        # Si tout échoue, on retourne un résultat FAILED générique
        return DeliveryResult(
            notification_id="unknown",
            user_id="unknown",
            channel="unknown",
            status=DeliveryStatus.FAILED,
            error=f"Retry exhausted: {last_error}",
        )


class FallbackMixin:
    """
    Fallback coopératif :
    - essaye les canaux dans un ordre
    - retourne la liste des résultats (un résultat par tentative)
    - s'arrête au premier SENT
    """

    def send_with_fallback(self, notification: Notification, user: User) -> List[DeliveryResult]:
        results: List[DeliveryResult] = []

        # Ordre préféré de l'utilisateur (sinon ordre par défaut)
        preferred = getattr(user.preferences, "enabled_channels", None) or ["sms", "email", "push"]

        for channel in preferred:
            # Respecter uniquement les canaux connus
            if channel not in ["sms", "email", "push"]:
                continue

            self.log(f"Trying channel={channel}")

            try:
                if channel == "sms":
                    r = self.send_sms(notification, user)
                elif channel == "email":
                    r = self.send_email(notification, user)
                else:
                    r = self.send_push(notification, user)

                results.append(r)

                # Stop au premier succès
                if r.status == DeliveryStatus.SENT:
                    self.log(f"Delivered successfully via {channel}")
                    return results

            except Exception as e:
                # Exception = cas où Retry aurait du sens
                self.log(f"Exception on channel {channel}: {e}")
                results.append(
                    DeliveryResult(
                        notification_id=notification.notification_id,
                        user_id=user.user_id,
                        channel=channel,
                        status=DeliveryStatus.FAILED,
                        error=str(e),
                    )
                )

        # Aucun canal n'a réussi
        return results
