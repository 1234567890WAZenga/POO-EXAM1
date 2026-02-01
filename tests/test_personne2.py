# tests/test_core.py
"""
Test global :
- preuve MRO (mixins)
- dispatch sur 2 notifications, ordre par priorité
"""

from __future__ import annotations

from core.models import User, UserPreferences, Notification, Priority
from core.emergencies import EmergencyType
from core.dispatcher import Dispatcher
from core.notifiers import EmergencyNotifier


def main():
    # Utilisateur avec ordre des canaux
    prefs = UserPreferences(enabled_channels=["sms", "email", "push"])
    user = User(user_id="agent1", email="guard@campus.edu", phone="0812345678", preferences=prefs)

    # Deux notifications, priorité différente
    n1 = Notification(emergency_type=EmergencyType.SECURITY, priority=Priority.LOW, message="Maintenance prévue")
    n2 = Notification(emergency_type=EmergencyType.SECURITY, priority=Priority.URGENT, message="Intrusion sur le campus")

    # Notifier concret
    notifier = EmergencyNotifier()

    # Preuve MRO
    print("MRO EmergencyNotifier:")
    print(EmergencyNotifier.__mro__)

    # Dispatch
    d = Dispatcher()
    d.schedule(n1, user, notifier)
    d.schedule(n2, user, notifier)

    results = d.dispatch()
    print("Résultats:")
    for r in results:
        print(r)

if __name__ == "__main__":
    main()
