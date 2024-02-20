from django.contrib import admin
from django.conf.locale.en import formats as en_formats

en_formats.DATE_FORMAT = "d M Y"

from .models import LoginServerAccounts
from .models import ServerAdminRegistration
from .models import ServerListType
from .models import WorldServerRegistration
from .models import Account


class LoginServerAccountsAdmin(admin.ModelAdmin):
    list_display = ["LoginServerID", "AccountName", "AccountEmail", "LastLoginDate", "ForumName"]
    list_filter = ["ForumName"]
    search_fields = ["AccountName", "ForumName"]
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
    list_display = ["ServerLongName", "ServerTagDescription", "ServerListTypeID", "ServerTrusted", "ServerAdminID",
                    "ServerLastLoginDate"]


class AccountAdmin(admin.ModelAdmin):
    list_display = ["name", "id", "lsaccount_id", "charname", "status"]
    list_filter = ["name"]
    search_fields = ["id", "name", "lsaccount_id"]
    readonly_fields = ["id", "active", "karma", "time_creation"]
    fieldsets = [
        ("General Information", {
            "fields": ["name", "charname", "lsaccount_id", "karma", "time_creation", "active"]
        }
         ),
        ("Flag Account as Mule/Trader", {"fields": ["mule"]}),
        ("Expansion Setting (Controls what expansions the account owns)", {"fields": ["expansion"]}),
        ("IP Exemptions", {"fields": ["ip_exemption_multiplier"]}),
        ("Administrative Actions",
         {"fields": ["revoked", "ban_reason", "suspendeduntil", "suspend_reason", "rulesflag"]}),
        ("GM Settings", {"fields": ["status", "gmspeed", "hideme", "gminvul", "flymode", "ignore_tells"]}),
    ]


admin.site.register(LoginServerAccounts, LoginServerAccountsAdmin)
admin.site.register(ServerAdminRegistration, ServerAdminRegistrationAdmin)
admin.site.register(ServerListType, ServerListTypeAdmin)
admin.site.register(WorldServerRegistration, WorldServerRegistrationAdmin)
admin.site.register(Account, AccountAdmin)
