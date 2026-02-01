"""
mixins/channels.py

Mixins de canaux (simulation) pour la démo.
But : prouver que l’héritage multiple + fallback + préférences fonctionnent.

Règles de simulation :
- SMS : nécessite user.phone
- Email : nécessite user.email
- Push : nécessite user.push_token

Chaque mixin renvoie un DeliveryResult.
"""

from __future__ import annotations

from typing import List

from core.models import DeliveryResult, DeliveryStatus, Notification, User


class LoggingMixin:
    """Ajoute un log simple. Peut être combiné avec d'autres mixins."""
    def log(self, message: str) -> None:
        print(f"[LOG] {message}")
        super().log(message)  # coopération MRO


class ChannelRegistryMixin:
    """
    Définit l’ordre des canaux supportés.
    Permet aussi au fallback de parcourir les canaux.
    """
    supported_channels = ["sms", "email", "push"]

    def get_supported_channels(self) -> List[str]:
        return list(self.supported_channels)


class SMSMixin:
    """Canal SMS simulé."""
    def send_sms(self, notification: Notification, user: User) -> DeliveryResult:
        if not user.phone:
            return DeliveryResult(
                notification_id=notification.notification_id,
                user_id=user.user_id,
                channel="sms",
                status=DeliveryStatus.FAILED,
                error="Phone manquant: SMS impossible",
            )

        # Ici on simule un succès
        return DeliveryResult(
            notification_id=notification.notification_id,
            user_id=user.user_id,
            channel="sms",
            status=DeliveryStatus.SENT,
            error=None,
        )


class EmailMixin:
    """Canal Email simulé."""
    def send_email(self, notification: Notification, user: User) -> DeliveryResult:
        if not user.email:
            return DeliveryResult(
                notification_id=notification.notification_id,
                user_id=user.user_id,
                channel="email",
                status=DeliveryStatus.FAILED,
                error="Email manquant: envoi email impossible",
            )

        return DeliveryResult(
            notification_id=notification.notification_id,
            user_id=user.user_id,
            channel="email",
            status=DeliveryStatus.SENT,
            error=None,
        )


class PushMixin:
    """Canal Push simulé."""
    def send_push(self, notification: Notification, user: User) -> DeliveryResult:
        if not user.push_token:
            return DeliveryResult(
                notification_id=notification.notification_id,
                user_id=user.user_id,
                channel="push",
                status=DeliveryStatus.FAILED,
                error="Push token manquant: push impossible",
            )

        return DeliveryResult(
            notification_id=notification.notification_id,
            user_id=user.user_id,
            channel="push",
            status=DeliveryStatus.SENT,
            error=None,
        )
