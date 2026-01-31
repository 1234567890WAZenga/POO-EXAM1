# mixins/channels.py
"""
Mixins de canaux (SMS/Email/Push) + LoggingMixin.

Objectif :
- comportements réutilisables
- héritage multiple + coopération via super()
- préparation d'une démonstration MRO claire

Cible (déduit du focus technique) :
- Sécurité Campus : canaux redondants, fallback, confirmation.
"""
from typing import Dict, List, Optional

from core.models import Channel, DeliveryResult, DeliveryStatus, Notification, User


class LoggingMixin:
    """
    Logging cooperatif :
    - on log ici puis on laisse les autres classes/mixins compléter via super().
    """
    def log(self, message: str) -> None:
        print(f"[LOG] {message}")
        # Appel cooperatif : si une autre classe plus loin définit log()
        # elle sera appelée (ou pas) selon le MRO.
        try:
            super().log(message)  # type: ignore[misc]
        except AttributeError:
            # Si personne d'autre n'implémente log(), on s'arrête proprement.
            pass


class ChannelRegistryMixin:
    """
    Mixin utilitaire : gère un registre local de canaux.
    """
    def __init__(self, *args, **kwargs):
        self._channels: Dict[str, Channel] = {}
        super().__init__(*args, **kwargs)  # coopération MRO

    def register_channel(self, channel: Channel) -> None:
        if not hasattr(channel, "name") or not channel.name:
            raise ValueError("Le channel doit avoir un attribut name non vide.")
        self._channels[channel.name] = channel

    def get_channel(self, name: str) -> Optional[Channel]:
        return self._channels.get(name)

    def list_channels(self) -> List[str]:
        return list(self._channels.keys())


class SMSMixin:
    """
    Ajoute la capacité d'envoyer via SMS.
    Suppose qu'un Channel nommé 'sms' est enregistré.
    """
    def send_sms(self, notification: Notification, user: User) -> DeliveryResult:
        ch = self.get_channel("sms")  # type: ignore[attr-defined]
        if ch is None:
            return DeliveryResult(
                notification_id=notification.notification_id,
                user_id=user.user_id,
                channel="sms",
                status=DeliveryStatus.FAILED,
                error="SMS channel not configured",
            )
        return ch.send(notification, user)


class EmailMixin:
    """
    Ajoute la capacité d'envoyer via Email.
    Suppose qu'un Channel nommé 'email' est enregistré.
    """
    def send_email(self, notification: Notification, user: User) -> DeliveryResult:
        ch = self.get_channel("email")  # type: ignore[attr-defined]
        if ch is None:
            return DeliveryResult(
                notification_id=notification.notification_id,
                user_id=user.user_id,
                channel="email",
                status=DeliveryStatus.FAILED,
                error="Email channel not configured",
            )
        return ch.send(notification, user)


class PushMixin:
    """
    Ajoute la capacité d'envoyer via Push.
    Suppose qu'un Channel nommé 'push' est enregistré.
    """
    def send_push(self, notification: Notification, user: User) -> DeliveryResult:
        ch = self.get_channel("push")  # type: ignore[attr-defined]
        if ch is None:
            return DeliveryResult(
                notification_id=notification.notification_id,
                user_id=user.user_id,
                channel="push",
                status=DeliveryStatus.FAILED,
                error="Push channel not configured",
            )
        return ch.send(notification, user)
