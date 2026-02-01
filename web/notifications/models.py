
from django.db import models


class NotificationLog(models.Model):
    """
    Enregistrement d'une notification envoyée depuis l'UI.

    Ce modèle ne remplace pas vos classes POO (core.models.Notification).
    Il sert uniquement à garder une trace pour l'historique web.
    """

    created_at = models.DateTimeField(auto_now_add=True)

    # Identité / contacts utilisateur (snapshot)
    user_id = models.CharField(max_length=100)
    email = models.CharField(max_length=200, blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    push_token = models.CharField(max_length=300, blank=True, default="")

    # Notification (snapshot)
    emergency_type = models.CharField(max_length=50)
    priority = models.CharField(max_length=10)
    message = models.TextField()
    zone = models.CharField(max_length=100, blank=True, default="")

    # Résumé : succès global ou non
    global_status = models.CharField(max_length=30, default="unknown")

    def __str__(self) -> str:
        return f"{self.created_at} | {self.emergency_type} {self.priority} -> {self.user_id}"


class DeliveryLog(models.Model):
    notification = models.ForeignKey(
        NotificationLog,
        on_delete=models.CASCADE,
        related_name="deliveries"
    )

    channel = models.CharField(max_length=30)
    status = models.CharField(max_length=30)  # sent/failed/pending_confirmation/confirmed
    error = models.TextField(blank=True, default="")
    delivery_id = models.CharField(max_length=64)

    # Confirmation
    confirmed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.channel} {self.status}"

