"""
This is the database router class for operations relating to tables found in the GameServer database.

For the purposes of this app, that should simply be the "accounts" model which ties the lsaccount_id
and forum_id to individual characters tied to a login server account and its overall forum id, respectively.
"""
from characters.models import Characters
from characters.models import CharacterCurrency
from characters.models import CharacterFactionValues
from characters.models import CharacterKeyring
from characters.models import CharacterLanguages
from characters.models import CharacterSpells
from characters.models import CharacterSkills
from characters.models import Guilds
from characters.models import GuildMembers
from characters.models import Items
from characters.models import SpellsNew


class GameServerRouter:
    """
    A router to control all database operations on LoginServer db models in the
    accounts application.
    """

    route_app_labels = {"characters"}
    game_server_models = [Characters,
                          CharacterCurrency,
                          CharacterFactionValues,
                          CharacterKeyring,
                          CharacterLanguages,
                          CharacterSkills,
                          CharacterSpells,
                          Guilds,
                          GuildMembers,
                          SpellsNew,
                          Items,]

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
        Allow relations if a model in the accounts app is
        involved.
        """
        if ((obj1._meta.app_label in self.route_app_labels or
             obj2._meta.app_label in self.route_app_labels
             ) and
            (obj1 in self.game_server_models and
              obj2 in self.game_server_models
             )
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the accounts app only appear in the
        'takp_ls_db' database.
        """
        if app_label in self.route_app_labels and model_name in self.game_server_models:
            return db == "game_database"
        return None
