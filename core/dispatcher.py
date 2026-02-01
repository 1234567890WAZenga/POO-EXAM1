"""
core/dispatcher.py

Dispatcher :
- Maintient une file de priorité basée sur Notification.priority
- Traite dans l'ordre URGENT -> LOW
- Appelle le notifier concret qui gère canaux + retry + fallback
"""
from dataclasses import dataclass
from typing import List

from core.models import Notification, User, DeliveryResult
from priority.priority_handler import PriorityQueue


@dataclass
class DispatchJob:
    """
    Un job = une notification à livrer à un user avec un notifier.
    """
    notification: Notification
    user: User
    notifier: object  # EmergencyNotifier ou autre


class Dispatcher:
    def __init__(self) -> None:
        self.priority_queue = PriorityQueue()

    def schedule(self, notification: Notification, user: User, notifier: object) -> None:
        """
        Ajoute un job dans la file en utilisant notification.priority.
        """
        job = DispatchJob(notification=notification, user=user, notifier=notifier)
        self.priority_queue.add(job, priority=notification.priority)

    def dispatch(self) -> List[DeliveryResult]:
        """
        Traite la file par priorité.
        Agrège tous les DeliveryResult.
        """
        all_results: List[DeliveryResult] = []

        while True:
            job = self.priority_queue.get_next()
            if job is None:
                break

            # notifier.send retourne une liste (tentatives fallback)
            results = job.notifier.send(job.notification, job.user)
            all_results.extend(results)

        return all_results
