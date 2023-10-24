"""
This is the database router class for operations relating to models belonging to
the login server database.
"""
from accounts.models import LoginServerAccounts
from accounts.models import ServerAdminRegistration
from accounts.models import ServerListType
from accounts.models import WorldServerRegistration


class LoginServerRouter:
    """
    A router to control all database operations on LoginServer db models in the
    accounts application.
    """

    route_app_labels = {"accounts"}
    login_server_models = [LoginServerAccounts,
                           ServerAdminRegistration,
                           ServerListType,
                           WorldServerRegistration]

    def db_for_read(self, model, **hints):
        """
        Attempts to read LoginServer models go to the login server database.
        """
        if ((model._meta.app_label in self.route_app_labels)
                and (model in self.login_server_models)):
            return "takp_ls"
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write LoginServer models go to the login server database.
        """
        if ((model._meta.app_label in self.route_app_labels)
                and (model in self.login_server_models)):
            return "takp_ls"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the accounts app is involved, and
        the model belongs to the login server database.
        """
        if ((obj1._meta.app_label in self.route_app_labels
                or obj2._meta.app_label in self.route_app_labels)
            and
            (obj1 in self.login_server_models
                and obj2 in self.login_server_models)
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the accounts app LoginServer models only appear in the
        login server database.
        """
        if (app_label in self.route_app_labels) and (model_name in self.login_server_models):
            return db == "takp_ls"
        return None
