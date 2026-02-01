"""
notifications/views.py

Rôle :
- UI : afficher dashboard (GET)
- Action : soumettre dispatch (POST)
- Cette couche ne fait pas de logique métier :
  elle appelle notifications/services.py
"""
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .forms import DispatchForm
from .services import dispatch_from_form


from django.shortcuts import get_object_or_404
from .models import NotificationLog

from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import DeliveryLog

from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    """
    GET /
    Affiche le formulaire + les résultats du dernier dispatch (session).
    """
    form = DispatchForm()
    results = request.session.pop("last_results", None)
    error = request.session.pop("last_error", None)

    return render(
        request,
        "notifications/dashboard.html",
        {"form": form, "results": results, "error": error},
    )

@login_required
@require_http_methods(["POST"])
def dispatch_submit(request):
    """
    POST /dispatch/
    Valide le formulaire, appelle le service, stocke les résultats en session,
    puis redirige vers / (dashboard).
    """
    form = DispatchForm(request.POST)
    if not form.is_valid():
        request.session["last_error"] = "Formulaire invalide."
        return redirect("dashboard")

    try:
        # Appel du pont Django -> Noyau POO
        results = dispatch_from_form(form.cleaned_data)

        # Stockage session pour affichage immédiat
        request.session["last_results"] = results

    except KeyError as e:
        # Typiquement : Enum EmergencyType ou Priority invalide
        request.session["last_error"] = f"Valeur Enum invalide: {e}"
    except Exception as e:
        # Toute autre erreur noyau
        request.session["last_error"] = str(e)

    return redirect("dashboard")

@login_required
def history(request):
    """
    UI : liste des notifications envoyées.
    """
    items = NotificationLog.objects.order_by("-created_at")[:200]
    return render(request, "notifications/history.html", {"items": items})

@login_required
def detail(request, notification_id: int):
    """
    UI : détails d'une notification + tentatives.
    """
    item = get_object_or_404(NotificationLog, pk=notification_id)
    deliveries = item.deliveries.all()
    return render(request, "notifications/detail.html", {"item": item, "deliveries": deliveries})

@require_http_methods(["POST"])
@login_required
def confirm_delivery(request, delivery_id: str):
    """
    Confirme une livraison à partir de delivery_id.
    Passe le statut à 'confirmed' et enregistre confirmed_at.
    """
    d = get_object_or_404(DeliveryLog, delivery_id=delivery_id)

    # Ne confirmer que si c'est logique
    if d.status in ["sent", "pending_confirmation"]:
        d.status = "confirmed"
        d.confirmed_at = timezone.now()
        d.save()

    # Retour vers la page détails de la notification
    return redirect("detail", notification_id=d.notification_id)
@login_required
@require_http_methods(["POST"])
def confirm_delivery(request, delivery_id: str):
    """
    Confirme une livraison à partir de delivery_id.
    Passe le statut à 'confirmed' et enregistre confirmed_at.
    """
    d = get_object_or_404(DeliveryLog, delivery_id=delivery_id)

    # Ne confirmer que si c'est logique
    if d.status in ["sent", "pending_confirmation"]:
        d.status = "confirmed"
        d.confirmed_at = timezone.now()
        d.save()

    # Retour vers la page détails de la notification
    return redirect("detail", notification_id=d.notification_id)
