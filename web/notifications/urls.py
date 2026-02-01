from django.urls import path
from .views import dashboard, dispatch_submit, history, detail
from .views import confirm_delivery

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("dispatch/", dispatch_submit, name="dispatch_submit"),
    path("history/", history, name="history"),
    path("history/<int:notification_id>/", detail, name="detail"),
      path("confirm/<str:delivery_id>/", confirm_delivery, name="confirm_delivery"),
]
