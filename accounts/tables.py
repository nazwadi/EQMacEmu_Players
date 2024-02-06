import django_tables2 as tables
from django_tables2.export.views import ExportMixin
from django_tables2.utils import Accessor
from .models import LoginServerAccounts


class LoginServerAccountTable(ExportMixin, tables.Table):
    AccountName = tables.LinkColumn("characters:list", args=[Accessor("AccountName")])
    update = tables.LinkColumn('accounts:update_account',
                               text="Update",
                               args=[Accessor('pk')],
                               attrs={'a': {'class': 'btn fa-regular fa-pen-to-square btn-outline-warning'}},
                               orderable=False)

    class Meta:
        model = LoginServerAccounts
        template_name = "django_tables2/bootstrap.html"
        fields = ("AccountName", "AccountEmail", "AccountCreateDate", "LastLoginDate")
        order_by = ("AccountName", "AccountCreateDate")
        orderable = True
