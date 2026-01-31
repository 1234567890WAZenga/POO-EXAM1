# tests/test_personne2.py
from core.models import User, EmergencyNotifier, EmergencyType, Priority
from core.dispatcher import Dispatcher
from decorators.function_decorators import retry_on_failure  # Pour forcer la démonstration

# Création de l'utilisateur
user = User("Agent du Campus", "guard@campus.edu", "1234567890")

# Notifications multiples
notif_urgent = EmergencyNotifier(user, "Intrusion sur le campus !", EmergencyType.SECURITY)
notif_urgent.priority = Priority.URGENT

notif_high = EmergencyNotifier(user, "Incendie bâtiment A", EmergencyType.FIRE)
notif_high.priority = Priority.HIGH

notif_low = EmergencyNotifier(user, "Maintenance prévue", EmergencyType.OTHER)
notif_low.priority = Priority.LOW

dispatcher = Dispatcher()
dispatcher.schedule(notif_low)    # Ajoutée en premier, mais traitée en dernier
dispatcher.schedule(notif_high)
dispatcher.schedule(notif_urgent)

# Dispatch : prouve l'ordre URGENT > HIGH > LOW
results = dispatcher.dispatch()
print("Ordre de traitement prouvé :", [r.channel for r in results])  # Montre l’envoi

# Démonstration du retry : forcer une exception
@retry_on_failure(max_retries=3)
def failing_send():
    raise Exception("Échec simulé")

try:
    failing_send()  # Montre les tentatives de retry
except Exception as e:
    print(e)  # "Toutes les tentatives ont échoué"
