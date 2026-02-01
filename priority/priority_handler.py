"""
priority/priority_handler.py

File de priorité stable.
- Utilise heapq
- Ordre : URGENT (4) en premier, LOW (1) en dernier
"""

from __future__ import annotations

import heapq
from typing import Any, List, Tuple

from core.models import Priority


class PriorityQueue:
    def __init__(self) -> None:
        self._heap: List[Tuple[int, int, Any]] = []
        self._index = 0

    def add(self, item: Any, priority: Priority) -> None:
        """
        heapq sort du plus petit au plus grand.
        Comme Priority.URGENT=4 doit passer en premier,
        on stocke la priorité négative.
        """
        heapq.heappush(self._heap, (-int(priority), self._index, item))
        self._index += 1

    def get_next(self) -> Any | None:
        if not self._heap:
            return None
        return heapq.heappop(self._heap)[2]
