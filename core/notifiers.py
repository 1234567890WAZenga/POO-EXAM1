"""
core/notifiers.py

Notificateur concret qui combine :
- Logging
- Registry canaux
- Retry
- Fallback
- Mixins canaux SMS/Email/Push
"""
from typing import List

from mixins.channels import LoggingMixin, ChannelRegistryMixin, SMSMixin, EmailMixin, PushMixin
from mixins.retry import RetryMixin, FallbackMixin
from core.models import BaseNotifier, Notification, User, DeliveryResult


class EmergencyNotifier(
    LoggingMixin,
    ChannelRegistryMixin,
    RetryMixin,
    FallbackMixin,
    SMSMixin,
    EmailMixin,
    PushMixin,
    BaseNotifier,
):
    __abstract__ = False

    def send(self, notification: Notification, user: User) -> List[DeliveryResult]:
        """
        Point d'entrée appelé par le Dispatcher.
        Retourne une liste de DeliveryResult (tentatives).
        """
        self.log("EmergencyNotifier.send called")
        return self.send_with_fallback(notification, user)
