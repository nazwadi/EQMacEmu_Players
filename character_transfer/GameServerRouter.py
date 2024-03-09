"""
This is the database router class for operations relating to tables found in the GameServer database.
"""
from accounts.models import Account
from common.models.characters import Characters


class GameServerRouter:
    """
    A router to control all database operations on LoginServer db models in the
    accounts application.
    """

    route_app_labels = {"character_transfer"}
    game_server_models = [Account,
                          Characters]

    def db_for_read(self, model, **hints):
        """
        Attempts to read LoginServerAccount models go to takp_ls_db.
        """
        if ((model._meta.app_label in self.route_app_labels)
                and (model in self.game_server_models)):
            return "game_database"
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write LoginServerAccount models go to takp_ls_db.
        """
        if ((model._meta.app_label in self.route_app_labels)
                and (model in self.game_server_models)):
            return "game_database"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the accounts app is involved.
        """
        if ((obj1._meta.app_label in self.route_app_labels
             or obj2._meta.app_label in self.route_app_labels)
                and
                (obj1 in self.game_server_models and obj2 in self.game_server_models)
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the character_transfer app only uses the game database.
        """
        if app_label in self.route_app_labels and model_name in self.game_server_models:
            return db == "game_database"
        return None
