from accounts.models import Account
from accounts.models import LoginServerAccounts
from common.models.characters import Characters


def valid_character_ownership(web_account: str, character_id: str) -> bool:
    """
    Returns True if the web account (ForumName) contains an account that
    owns a character with the given character_id

    :param web_account: web account name
    :param character_id: character's unique id from the character_data table
    :return: True if the character belongs to a game account managed by that web account
    """
    ls_accounts = LoginServerAccounts.objects.filter(ForumName=web_account)
    target_character = Characters.objects.filter(id=character_id).first()
    ls_account_names = list()
    for account_name in ls_accounts.values('AccountName'):
        ls_account_names.append(account_name['AccountName'])
        game_account = Account.objects.filter(name=account_name['AccountName'])
        if game_account.exists():
            try:
                game_account_id = game_account.values('id')[0]
            except IndexError:
                continue

            if game_account_id is not None:
                characters = Characters.objects.filter(account_id=game_account_id['id'])
                for character in characters:
                    if character.id == target_character.id:
                        return True
    return False
