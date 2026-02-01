from django import forms
from core.emergencies import EmergencyType
from core.models import Priority


class DispatchForm(forms.Form):
    """
    Formulaire de déclenchement d'une notification.
    Rôle :
    - valider les entrées utilisateur (UI)
    - préparer les données pour le noyau POO (core/)
    """

    # =========================
    # Informations utilisateur
    # =========================

    user_id = forms.CharField(
        label="Identifiant utilisateur",
        max_length=100,
        help_text="Identifiant logique de l’utilisateur (ex : agent_campus_1)"
    )

    email = forms.EmailField(
        label="Adresse email",
        required=False,
        help_text="Utilisé si le canal Email est disponible"
    )

    phone = forms.CharField(
        label="Numéro de téléphone",
        required=False,
        max_length=30,
        help_text="Utilisé pour les notifications SMS"
    )

    push_token = forms.CharField(
        label="Token Push",
        required=False,
        max_length=200,
        help_text="Utilisé pour les notifications Push"
    )

    # =========================
    # Notification
    # =========================

    emergency_type = forms.ChoiceField(
        label="Type d’urgence",
        choices=[(e.name, e.name) for e in EmergencyType],
        help_text="Sélectionnez le type d’événement critique"
    )

    priority = forms.ChoiceField(
        label="Priorité",
        choices=[(p.name, p.name) for p in Priority],
        help_text="URGENT > HIGH > MEDIUM > LOW"
    )

    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={"rows": 5}),
        help_text="Contenu de la notification"
    )

    zone = forms.CharField(
        label="Zone concernée",
        required=False,
        max_length=100,
        help_text="Zone ou bâtiment concerné (optionnel)"
    )
