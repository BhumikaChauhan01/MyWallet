from django.urls import path
from . import views

urlpatterns = [
    path("register/" , views.register_view , name="register"),
    path("" , views.dashboard_view , name="dashboard"),
    path("transaction/add/", views.transaction_view, name="transaction_add"),
    path("transaction/", views.transactionlist_view, name="transaction_list"),
    path("goal/add/", views.goal_view, name="goal_add"),
    path("generate_report" , views.export_transactions , name = "export_transactions")

]
