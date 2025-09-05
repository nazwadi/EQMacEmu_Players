from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("", views.index_request, name="index"),
    path("inventory_search", views.inventory_search, name="inventory_search"),
    path("register", views.register_request, name="register"),
    path("login", views.login_request, name="login"),
    path("logout/", views.logout_request, name="logout"),
    path("list", views.accounts, name="list_accounts"),
    path("server_list", views.server_list, name="server_list"),
    path("create", views.create_account, name="create_account"),
    path("delete/<int:pk>", views.delete_account, name="delete_account"),
    path("update/<int:pk>", views.update_account, name="update_account"),
    path('convert-to-trader/', views.convert_to_trader, name='convert_to_trader'),
]
