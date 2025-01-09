from django.urls import path
from .views import BonusView, TransactionView, LoginView

urlpatterns = [
    path("login/auth/", LoginView.as_view(), name="login_auth"),
    path("users/bonus/", BonusView.as_view(), name="user_bonus"),
    path("users/transactions/", TransactionView.as_view(), name="add_transaction"),
]
