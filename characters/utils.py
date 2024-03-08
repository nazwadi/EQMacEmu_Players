from dataclasses import dataclass
from enum import Enum
from accounts.models import Account
from accounts.models import LoginServerAccounts


class FactionValue(Enum):
    FACTION_MAX_ALLY = 0
    FACTION_ALLY = 1
    FACTION_WARMLY = 2
    FACTION_KINDLY = 3
    FACTION_AMIABLY = 4
    FACTION_INDIFFERENTLY = 5
    FACTION_APPREHENSIVELY = 6
    FACTION_DUBIOUSLY = 7
    FACTION_THREATENINGLY = 8
    FACTION_SCOWLS = 9
    FACTION_MAX_SCOWLS = 10


def faction_value_to_string(faction_value: FactionValue) -> str:
    match faction_value:
        case FactionValue.FACTION_MAX_ALLY:
            return "Max Ally"
        case FactionValue.FACTION_ALLY:
            return "Ally"
        case FactionValue.FACTION_WARMLY:
            return "Warmly"
        case FactionValue.FACTION_KINDLY:
            return "Kindly"
        case FactionValue.FACTION_AMIABLY:
            return "Amiably"
        case FactionValue.FACTION_INDIFFERENTLY:
            return "Indifferently"
        case FactionValue.FACTION_APPREHENSIVELY:
            return "Apprehensively"
        case FactionValue.FACTION_DUBIOUSLY:
            return "Dubiously"
        case FactionValue.FACTION_THREATENINGLY:
            return "Threateningly"
        case FactionValue.FACTION_SCOWLS:
            return "Scowls"

    return "Unknown"


@dataclass
class FactionMod:
    """Class to keep track of faction modifiers"""
    base_mod: int = 0
    race_mod: int = 0
    class_mod: int = 0
    deity_mod: int = 0

    def calculate_faction(self, tmp_character_value: int) -> FactionValue:
        """
        Calculate the faction level given a set of faction modifiers and character base faction
        Values for each level were derived from EQMacEmu source code as of 8 March 2024.

        :param tmp_character_value: a character's base faction with any spell or item modifiers
        :return: the faction level as an enum
        """
        character_value: int = tmp_character_value + self.base_mod + self.class_mod + self.race_mod + self.deity_mod

        if character_value >= 2000:
            return FactionValue.FACTION_MAX_ALLY
        elif character_value >= 1100:
            return FactionValue.FACTION_ALLY
        elif 750 <= character_value <= 1099:
            return FactionValue.FACTION_WARMLY
        elif 500 <= character_value <= 749:
            return FactionValue.FACTION_KINDLY
        elif 100 <= character_value <= 499:
            return FactionValue.FACTION_AMIABLY
        elif 0 <= character_value <= 99:
            return FactionValue.FACTION_INDIFFERENTLY
        elif -100 <= character_value <= -1:
            return FactionValue.FACTION_APPREHENSIVELY
        elif -500 <= character_value <= -101:
            return FactionValue.FACTION_DUBIOUSLY
        elif -750 <= character_value <= -501:
            return FactionValue.FACTION_THREATENINGLY
        elif character_value <= -751:
            return FactionValue.FACTION_SCOWLS
        elif character_value <= -2000:
            return FactionValue.FACTION_MAX_SCOWLS
        else:
            return FactionValue.FACTION_INDIFFERENTLY


def valid_game_account_owner(web_account: str, game_account_name: str) -> bool:
    """
    Returns True if the web account (ForumName) owns the game account

    :param web_account:
    :param game_account_name:
    :return: bool
    """
    game_account = Account.objects.filter(name=game_account_name)
    ls_account = LoginServerAccounts.objects.filter(ForumName=web_account)

    try:
        game_account_name = game_account.values('name')[0]
    except IndexError:
        return False

    # Ensure the requested game account belongs to the current user
    ls_account_names = []
    for account_name in ls_account.values('AccountName'):
        ls_account_names.append(account_name['AccountName'])

    if game_account_name['name'] not in ls_account_names:
        return False

    return True
