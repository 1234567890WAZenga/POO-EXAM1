
from priority.priority_handler import PriorityQueue
# Supposons des imports depuis d'autres fichiers :
# ex. from core.models import DeliveryResult, BaseNotifier

class Dispatcher:
    def __init__(self):
        self.priority_queue = PriorityQueue()
        self.channels = ['SMS', 'Email', 'Push']  # Ordre de repli (fallback)

    # Partie ordonnancement (ta responsabilité)
    def schedule(self, notifier):
        """
        Ajoute un notifier à la file de priorité.
        Générique : accepte tout type de notifier.
        Optimisé : pour la sécurité du campus, priorise URGENT
        (ex. : alerte d’intrusion).
        """
        self.priority_queue.add(notifier)

    def dispatch(self):
        """
        Traite la file par ordre de priorité.
        Pour chaque notifier : essaie les canaux disponibles avec mécanisme de repli.
        """
        results = []
        while notifier := self.priority_queue.get_next():
            success = False
            for channel in self.channels:
                if notifier.user.preferences.opt_in.get(channel, False):
                    try:
                        notifier.send(notifier.message)  # Utilise les décorateurs et mixins
                        results.append(DeliveryResult(success=True, channel=channel))
                        success = True
                        break
                    except Exception as e:
                        print(f"Repli depuis le canal {channel} dans le contexte de la sécurité du campus : {e}")
            if not success:
                results.append(DeliveryResult(success=False, channel="Tous les canaux ont échoué"))
        return results

