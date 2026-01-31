import functools

def log_notification(func):
    """
    Décorateur pour journaliser les notifications.
    Générique : journalise tout appel à send().
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Journalisation de la notification dans le contexte de la sécurité du campus : {args}, {kwargs}")
        return func(*args, **kwargs)
    return wrapper

def retry_on_failure(max_retries=3):
    """
    Décorateur pour réessayer en cas d'échec.
    Optimisé : pour la sécurité du campus, retries plus agressifs en cas d'URGENCE.
    Reste toutefois générique.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = max_retries
            # Optionnel : augmente le nombre de tentatives pour les priorités élevées (ex : urgence campus)
            if 'priority' in kwargs and kwargs['priority'] == 'URGENT':
                retries += 2  # Optimisation pour la sécurité du campus
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Tentative {attempt + 1} échouée dans la sécurité du campus : {e}")
            raise Exception("Toutes les tentatives ont échoué dans le contexte de la sécurité du campus")
        return wrapper
    return decorator

