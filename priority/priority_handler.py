import heapq
from enum import Enum

class Priority(Enum):
    URGENT = 0  # Ex : intrusion sur le campus
    HIGH = 1    # Ex : incendie
    MEDIUM = 2  # Ex : alerte médicale
    LOW = 3     # Ex : maintenance

class PriorityQueue:
    """
    File de priorité basée sur heapq.
    Générique : utilisable pour tout système de notification.
    Optimisée : basée sur l'énumération Priority, idéale pour trier des alertes de campus.
    """
    def __init__(self):
        self.queue = []  # (valeur_priorité, index, notifier) pour éviter les égalités
        self.index = 0

    def add(self, notifier):
        heapq.heappush(self.queue, (notifier.priority.value, self.index, notifier))
        self.index += 1

    def get_next(self):
        if self.queue:
            return heapq.heappop(self.queue)[2]
        return None

