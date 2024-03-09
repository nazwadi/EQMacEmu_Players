from accounts.models import Account
from accounts.models import LoginServerAccounts


def valid_game_account_owner(web_account: str, game_account_id: str) -> bool:
    """
    Returns True if the web account (ForumName) owns the game account

    :param web_account:
    :param game_account_id:
    :return: bool
    """
    game_account = Account.objects.filter(id=game_account_id)
    ls_account = LoginServerAccounts.objects.filter(ForumName=web_account)

    try:
        game_account_name = game_account.values('name')[0]
    except IndexError:
        return False

    # Ensure the requested game account belongs to the current user
    ls_account_names = []
    for account_name in ls_account.values('AccountName'):
        ls_account_names.append(account_name['AccountName'])

    return game_account_name['name'] in ls_account_names
