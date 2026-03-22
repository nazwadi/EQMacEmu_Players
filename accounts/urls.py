from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

app_name = "accounts"
urlpatterns = [
    path("", views.index_request, name="index"),
    path("inventory_search", views.inventory_search, name="inventory_search"),
    path("register", views.register_request, name="register"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name="logout"),
    path("list", views.accounts, name="list_accounts"),
    path("server_list", views.server_list, name="server_list"),
    path("create", views.create_account, name="create_account"),
    path("delete/<int:pk>", views.delete_account, name="delete_account"),
    path("update/<int:pk>", views.update_account, name="update_account"),
    path('convert-to-trader/', views.convert_to_trader, name='convert_to_trader'),

    path('login-history/', views.login_history, name='login_history'),
    path('sessions/', views.session_management, name='session_management'),

    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             template_name='accounts/password_change_form.html',
             success_url=reverse_lazy('accounts:password_change_done'),
         ),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='accounts/password_change_done.html',
         ),
         name='password_change_done'),

    path('mfa/verify/', views.mfa_verify, name='mfa_verify'),
    path('mfa/setup/', views.mfa_setup, name='mfa_setup'),
    path('mfa/backup-codes/', views.mfa_backup_codes, name='mfa_backup_codes'),
    path('mfa/disable/', views.mfa_disable, name='mfa_disable'),

    # Password reset URLs
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset_form.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url=reverse_lazy('accounts:password_reset_done'),

         ),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html',
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url=reverse_lazy('accounts:password_reset_complete'),
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
