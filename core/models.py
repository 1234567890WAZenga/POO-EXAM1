 
# core/models.py
"""
Modèles métier minimalistes pour la phase POO (sans Web/Docker).

Objectif :
- fournir des structures stables pour que les Mixins/Notifiers/Dispatcher
  puissent fonctionner.
- permettre la démonstration : priorité, canaux, confirmation.

Cible de groupe (déduit du focus technique) :
- Sécurité Campus : priorité, redondance, confirmation de livraison.
"""
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional
import time
import uuid

from core.emergencies import EmergencyType


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class DeliveryStatus(str, Enum):
    SENT = "sent"
    FAILED = "failed"
    PENDING_CONFIRMATION = "pending_confirmation"
    CONFIRMED = "confirmed"


@dataclass
class Notification:
    """
    Notification à livrer.
    - emergency_type : type d'urgence
    - priority : niveau (LOW..URGENT)
    - message : contenu
    - zone : zone ciblée (optionnel)
    - meta : données additionnelles (optionnel)
    """
    emergency_type: EmergencyType
    priority: Priority
    message: str
    zone: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)
    notification_id: str = field(default_factory=lambda: uuid.uuid4().hex)


@dataclass
class UserPreferences:
    """
    Préférences utilisateur :
    - enabled_channels : ordre préféré des canaux (ex: ["sms","email","push"])
    - opt_out_types : types d'urgence désactivés (ex: [EmergencyType.ACADEMIC])
    - language : langue préférée (optionnel)
    """
    enabled_channels: List[str] = field(default_factory=lambda: ["sms", "email", "push"])
    opt_out_types: List[EmergencyType] = field(default_factory=list)
    language: str = "fr"


@dataclass
class User:
    """
    Utilisateur cible.
    Pour la phase POO, on garde simple et compatible:
    - email, phone, push_token : contacts
    - preferences : préférences de réception
    """
    user_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    push_token: Optional[str] = None
    preferences: UserPreferences = field(default_factory=UserPreferences)


@dataclass
class DeliveryResult:
    """
    Résultat d'une tentative d'envoi.
    delivery_id sert pour la confirmation.
    """
    notification_id: str
    user_id: str
    channel: str
    status: DeliveryStatus
    delivery_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class Channel:
    """
    Interface simple de canal.
    Les canaux concrets (SMS/Email/Push) peuvent être des implémentations réelles
    ou simulées (phase POO).
    """
    name: str = "channel"

    def send(self, notification: Notification, user: User) -> DeliveryResult:
        raise NotImplementedError("Channel.send doit être implémentée.")


class BaseNotifier:
    """
    Classe de base des notificateurs.
    - Pensée pour être combinée avec des Mixins (héritage multiple).
    - __abstract__ permet à la métaclasse (plus tard) d'éviter l'enregistrement.

    Contrat :
    - send(notification, user) -> List[DeliveryResult]
    """
    __abstract__ = True

    def log(self, message: str) -> None:
        # Implémentation par défaut, peut être enrichie par LoggingMixin
        print(message)

    def send(self, notification: Notification, user: User) -> List[DeliveryResult]:
        """
        Base minimaliste : à surcharger par les Mixins et/ou un dispatcher.
        """
        raise NotImplementedError("BaseNotifier.send doit être fourni par un notificateur concret.")
