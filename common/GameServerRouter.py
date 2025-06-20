"""
This is the database router class for operations relating to tables found in the GameServer database.
"""
from common.models.characters import Characters, CharacterAlternateAbility
from common.models.characters import CharacterCurrency
from common.models.characters import CharacterFactionValues
from common.models.characters import CharacterInventory
from common.models.characters import CharacterKeyring
from common.models.characters import CharacterLanguages
from common.models.characters import CharacterSpells
from common.models.characters import CharacterSkills
from common.models.faction import FactionList
from common.models.faction import FactionListMod
from common.models.guilds import Guilds
from common.models.guilds import GuildMembers
from common.models.items import DiscoveredItems
from common.models.items import Items
from common.models.loot import LootTable
from common.models.loot import LootTableEntries
from common.models.loot import LootDropEntries
from common.models.npcs import MerchantList
from common.models.npcs import MerchantListTemp
from common.models.npcs import NPCFaction
from common.models.npcs import NPCSpellsEntries
from common.models.npcs import NPCTypes
from common.models.tradeskill import TradeskillRecipe
from common.models.tradeskill import TradeskillRecipeEntries
from common.models.spawns import SpawnEntry
from common.models.spawns import SpawnGroup
from common.models.spawns import Spawn2
from common.models.spells import SpellsNew
from common.models.zones import Zone
from common.models.zones import ZonePoints


class GameServerRouter:
    """
    A router to control all database operations on db models in the application.
    """

    route_app_labels = {"common"}
    game_server_models = [Characters,
                          CharacterAlternateAbility,
                          CharacterCurrency,
                          CharacterFactionValues,
                          CharacterInventory,
                          CharacterKeyring,
                          CharacterLanguages,
                          CharacterSkills,
                          CharacterSpells,
                          DiscoveredItems,
                          FactionList,
                          FactionListMod,
                          Guilds,
                          GuildMembers,
                          LootTable,
                          LootTableEntries,
                          LootDropEntries,
                          MerchantList,
                          MerchantListTemp,
                          NPCFaction,
                          NPCTypes,
                          NPCSpellsEntries,
                          TradeskillRecipe,
                          TradeskillRecipeEntries,
                          SpawnEntry,
                          SpawnGroup,
                          Spawn2,
                          SpellsNew,
                          Items,
                          Zone,
                          ZonePoints]

    def db_for_read(self, model, **hints):
        """
        Attempts to read models go to the game database
        """
        if ((model._meta.app_label in self.route_app_labels)
                and (model in self.game_server_models)):
            return "game_database"
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write models go to the game database
        """
        if ((model._meta.app_label in self.route_app_labels)
                and (model in self.game_server_models)):
            return "game_database"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the common app is involved.
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
        Make sure the common app models only appear in the game database.
        """
        if app_label in self.route_app_labels and model_name in self.game_server_models:
            return db == "game_database"
        return None
