
from typing import Any, Dict, List

from core.models import User, Notification, Priority
from core.emergencies import EmergencyType
from core.dispatcher import Dispatcher
from core.notifiers import EmergencyNotifier

from .models import NotificationLog, DeliveryLog


def _parse_emergency_type(raw: str) -> EmergencyType:
    key = raw.strip().upper()
    return EmergencyType[key]


def _parse_priority(raw: str) -> Priority:
    key = raw.strip().upper()
    return Priority[key]


def dispatch_from_form(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Pont Django -> noyau POO + persistance en DB (historique).

    1) Construire User + Notification (objets métier)
    2) Appeler Dispatcher + EmergencyNotifier (moteur POO)
    3) Logger NotificationLog + DeliveryLog en SQLite
    4) Retourner résultats sérialisés pour l'UI
    """

    # 1) User (métier)
    user = User(
        user_id=data["user_id"],
        email=data.get("email") or None,
        phone=data.get("phone") or None,
        push_token=data.get("push_token") or None,
    )

    # 2) Notification (métier)
    emergency_type = _parse_emergency_type(data["emergency_type"])
    priority = _parse_priority(data["priority"])

    notif = Notification(
        emergency_type=emergency_type,
        priority=priority,
        message=data["message"],
        zone=data.get("zone") or None,
    )

    # 3) Moteur POO
    notifier = EmergencyNotifier()
    dispatcher = Dispatcher()

    dispatcher.schedule(notification=notif, user=user, notifier=notifier)
    results = dispatcher.dispatch()

    # 4) Statut global simple : au moins une livraison "sent" => sent, sinon failed
    serialized = []
    has_sent = False

    for r in results:
        status_str = r.status.value if hasattr(r.status, "value") else str(r.status)
        if status_str == "sent":
            has_sent = True

        serialized.append(
            {
                "notification_id": r.notification_id,
                "user_id": r.user_id,
                "channel": r.channel,
                "status": status_str,
                "error": r.error,
                "delivery_id": r.delivery_id,
            }
        )

    global_status = "sent" if has_sent else "failed"

    # 5) Persister en DB (snapshot)
    nlog = NotificationLog.objects.create(
        user_id=user.user_id,
        email=user.email or "",
        phone=user.phone or "",
        push_token=user.push_token or "",
        emergency_type=emergency_type.name,
        priority=priority.name,
        message=notif.message,
        zone=notif.zone or "",
        global_status=global_status,
    )

    for row in serialized:
        DeliveryLog.objects.create(
            notification=nlog,
            channel=row["channel"],
            status=row["status"],
            error=row["error"] or "",
            delivery_id=row["delivery_id"],
        )

    return serialized
