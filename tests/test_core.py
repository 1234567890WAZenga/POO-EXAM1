# Exemple de notificateur concret pour démo MRO (à placer où vous voulez)
from mixins.channels import LoggingMixin, ChannelRegistryMixin, SMSMixin, EmailMixin, PushMixin
from mixins.retry import RetryMixin, FallbackMixin
from core.models import BaseNotifier, Notification, User

class EmergencyNotifier(
    LoggingMixin,
    ChannelRegistryMixin,
    RetryMixin,
    FallbackMixin,
    SMSMixin,
    EmailMixin,
    PushMixin,
    BaseNotifier
):
    __abstract__ = False

    def send(self, notification: Notification, user: User):
        # Point central: appelle le fallback qui exploite les capacités injectées par mixins
        self.log("EmergencyNotifier.send called")
        return self.send_with_fallback(notification, user)

# Preuve MRO
print(EmergencyNotifier.__mro__)
