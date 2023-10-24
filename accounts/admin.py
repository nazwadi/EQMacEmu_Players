from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import LoginServerAccounts
from .models import ServerAdminRegistration
from .models import ServerListType
from .models import WorldServerRegistration


class LoginServerAccountsAdmin(admin.ModelAdmin):
    list_display = ["LoginServerID", "AccountName", "AccountEmail", "LastLoginDate", "ForumName"]
    list_filter = ["ForumName"]
    fieldsets = [
        ("User Self-Registration", {"fields": ["AccountName", "AccountPassword", "AccountEmail", "ForumName"]}),
        ("Admin Settings", {"fields": ["client_unlock", "max_accts", "Num_IP_Bypass"]}),
        ("Location", {"fields": ["LastIPAddress", "creationIP"]}),
    ]


class ServerAdminRegistrationAdmin(admin.ModelAdmin):
    list_display = ["ServerAdminID", "AccountName", "Email", "RegistrationDate", "RegistrationIPAddr"]


class ServerListTypeAdmin(admin.ModelAdmin):
    ordering = ('ServerListTypeID',)
    list_display = ["ServerListTypeID", "ServerListTypeDescription"]


class WorldServerRegistrationAdmin(admin.ModelAdmin):
    list_display = ["ServerLongName", "ServerTagDescription", "ServerListTypeID", "ServerTrusted", "ServerAdminID", "ServerLastLoginDate"]


admin.site.register(LoginServerAccounts, LoginServerAccountsAdmin)
admin.site.register(ServerAdminRegistration, ServerAdminRegistrationAdmin)
admin.site.register(ServerListType, ServerListTypeAdmin)
admin.site.register(WorldServerRegistration, WorldServerRegistrationAdmin)

