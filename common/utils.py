import math
from accounts.models import Account
from accounts.models import LoginServerAccounts


def valid_game_account_owner(web_account: str, game_account_id: str) -> bool:
    """
    Returns True if the web account (ForumName) owns the game account

    :param web_account:
    :param game_account_id:
    :return: bool
    """
    game_account = Account.objects.filter(id=game_account_id).first()
    ls_account = LoginServerAccounts.objects.filter(ForumName__iexact=web_account)

    if game_account is None or ls_account is None:
        return False

    # Ensure the requested game account belongs to the current user
    ls_account_names = []
    for account_name in ls_account.values('AccountName'):
        ls_account_names.append(account_name['AccountName'].lower())

    return game_account.name.lower() in ls_account_names


def calculate_item_price(item_price: int):
    """
    Takes the item price in copper and returns the price in platinum, gold, silver, and copper

    :param item_price: an integer value in units of copper
    :return: a list of platinum, gold, silver, and copper
    """
    platinum = math.floor(item_price / 1000),
    gold = math.floor((item_price % 1000) / 100),
    silver = math.floor((item_price % 100) / 10),
    copper = item_price % 10

    return platinum, gold, silver, copper
