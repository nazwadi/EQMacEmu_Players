"""
Management command to create a stub EverQuest character in the game database
for local development and feature testing.

Usage:
    python manage.py create_stub_character
    python manage.py create_stub_character --name Soandso --account-id 1
    python manage.py create_stub_character --delete Soandso

The default stub is a level 60 Dark Elf Wizard named Soandso.
"""

from django.core.management.base import BaseCommand
from django.db import connections

from magelo.models import CharacterPermissions


# ---------------------------------------------------------------------------
# Stub profile — level 60 Dark Elf Wizard
# Base stats below are without gear. The Magelo view adds item bonuses on top.
# ---------------------------------------------------------------------------
STUB_DEFAULTS = {
    'last_name': '',
    'title': '',
    'suffix': '',
    'zone_id': 1,           # qeynos (harmless default)
    'gender': 0,
    'race': 6,              # Dark Elf
    'class_name': 12,       # Wizard
    'level': 60,
    'deity': 204,           # Cazic-Thule
    'anon': 0,
    'gm': 0,
    'face': 0,
    'hair_color': 0,
    'hair_style': 0,
    'beard': 0,
    'beard_color': 0,
    'eye_color_1': 0,
    'eye_color_2': 0,
    'exp': 1580443960,      # max exp at 60
    'aa_points_spent': 150,
    'aa_exp': 0,
    'aa_points': 10,
    # Base stats (without gear). Typical level 60 DE Wiz allocation.
    'str': 75,
    'sta': 95,
    'cha': 75,
    'dex': 95,
    'int_stat': 160,
    'agi': 95,
    'wis': 80,
    'cur_hp': 2000,
    'mana': 3500,
    'endurance': 500,
    'hunger_level': 6000,
    'thirst_level': 6000,
    'is_deleted': 0,
    'showhelm': 1,
    'firstlogon': 0,
}

# Skills: (skill_id, value)
#   15 = Defense, 33 = Offense
#   Values are approximate max for a level 60 Wizard
STUB_SKILLS = [
    (15, 200),   # Defense
    (33, 85),    # Offense
]


class Command(BaseCommand):
    help = 'Create (or delete) a stub EverQuest character for local development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            default='Soandso',
            help='Character name (default: Soandso)',
        )
        parser.add_argument(
            '--account-id',
            type=int,
            default=None,
            help='Game account ID to assign the character to. If omitted, one is resolved '
                 'from --web-user or created automatically.',
        )
        parser.add_argument(
            '--web-user',
            default=None,
            help='Web username (auth.User) to link the character to. The command will '
                 'look up or create the matching game account automatically.',
        )
        parser.add_argument(
            '--delete',
            metavar='NAME',
            help='Delete the stub character with this name instead of creating one',
        )

    def handle(self, *args, **options):
        if options['delete']:
            self._delete(options['delete'])
        else:
            account_id = options['account_id']
            if account_id is None:
                account_id = self._resolve_account(options['web_user'])
            self._create(options['name'], account_id)

    def _resolve_account(self, web_user):
        """
        Find or create a game account linked to a web user.

        Walks the chain: auth.User → LoginServerAccounts → Account (game DB).
        If no game Account exists for the user's LoginServerID, creates a stub one.
        Falls back to account_id=0 if no web_user is given.
        """
        if not web_user:
            self.stdout.write(self.style.WARNING(
                'No --web-user given; using account_id=0. '
                'Character will not be tied to any web account.'
            ))
            return 0

        from django.contrib.auth import get_user_model
        from accounts.models import Account, LoginServerAccounts

        User = get_user_model()
        if not User.objects.filter(username=web_user).exists():
            self.stdout.write(self.style.ERROR(f'Web user "{web_user}" not found in auth_user.'))
            raise SystemExit(1)

        ls = LoginServerAccounts.objects.filter(ForumName=web_user).first()
        if ls is None:
            self.stdout.write(self.style.ERROR(
                f'No LoginServerAccount found for web user "{web_user}". '
                f'The user must have logged in to the game server at least once.'
            ))
            raise SystemExit(1)

        self.stdout.write(f'  Found LoginServerAccount: LoginServerID={ls.LoginServerID}, AccountName={ls.AccountName}')

        account = Account.objects.filter(lsaccount_id=ls.LoginServerID).first()
        if account:
            self.stdout.write(f'  Found existing game account: id={account.id}, name={account.name}')
            return account.id

        # No game account yet — create a stub one
        db = connections['game_database']
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO account (name, lsaccount_id, status, gmspeed, revoked, minilogin_ip) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                [ls.AccountName, ls.LoginServerID, 0, 0, 0, '']
            )
            account_id = cur.lastrowid
        self.stdout.write(self.style.SUCCESS(f'  Created stub game account: id={account_id}, name={ls.AccountName}'))
        return account_id

    # ------------------------------------------------------------------

    def _delete(self, name):
        db = connections['game_database']
        with db.cursor() as cur:
            cur.execute("SELECT id FROM character_data WHERE name = %s", [name])
            row = cur.fetchone()
        if row is None:
            self.stdout.write(self.style.WARNING(f'Character "{name}" not found.'))
            return

        char_id = row[0]
        with db.cursor() as cur:
            cur.execute("DELETE FROM character_skills WHERE id = %s", [char_id])
            cur.execute("DELETE FROM character_currency WHERE id = %s", [char_id])
            cur.execute("DELETE FROM character_data WHERE id = %s", [char_id])
        CharacterPermissions.objects.filter(character_name=name).delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted stub character "{name}" (id={char_id}).'))

    def _create(self, name, account_id):
        db = connections['game_database']
        with db.cursor() as cur:
            cur.execute("SELECT id FROM character_data WHERE name = %s", [name])
            if cur.fetchone() is not None:
                self.stdout.write(self.style.WARNING(
                    f'Character "{name}" already exists. Use --delete {name} first to recreate.'
                ))
                return

        # Use raw SQL so we only touch columns that actually exist in the game
        # DB table. The Characters Django model has extra fields (e.g. forum_id)
        # that don't exist on all server versions.
        db = connections['game_database']
        s = STUB_DEFAULTS
        with db.cursor() as cur:
            cur.execute("""
                INSERT INTO character_data (
                    account_id, name, last_name, title, suffix,
                    zone_id, gender, race, `class`, level, deity,
                    anon, gm, face, hair_color, hair_style,
                    beard, beard_color, eye_color_1, eye_color_2,
                    exp, aa_points_spent, aa_exp, aa_points,
                    str, sta, cha, dex, `int`, agi, wis,
                    cur_hp, mana, endurance,
                    hunger_level, thirst_level,
                    is_deleted, showhelm, firstlogon
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, %s, %s
                )
            """, [
                account_id, name, s['last_name'], s['title'], s['suffix'],
                s['zone_id'], s['gender'], s['race'], s['class_name'], s['level'], s['deity'],
                s['anon'], s['gm'], s['face'], s['hair_color'], s['hair_style'],
                s['beard'], s['beard_color'], s['eye_color_1'], s['eye_color_2'],
                s['exp'], s['aa_points_spent'], s['aa_exp'], s['aa_points'],
                s['str'], s['sta'], s['cha'], s['dex'], s['int_stat'], s['agi'], s['wis'],
                s['cur_hp'], s['mana'], s['endurance'],
                s['hunger_level'], s['thirst_level'],
                s['is_deleted'], s['showhelm'], s['firstlogon'],
            ])
            char_id = cur.lastrowid

        self.stdout.write(f'  Created character "{name}" with id={char_id}')

        # Insert skills via raw SQL — CharacterSkills has a composite PK
        # that the Django model doesn't represent, so raw SQL is safer here.
        db = connections['game_database']
        with db.cursor() as cur:
            for skill_id, value in STUB_SKILLS:
                cur.execute(
                    "INSERT INTO character_skills (id, skill_id, value) VALUES (%s, %s, %s)",
                    [char_id, skill_id, value],
                )
        self.stdout.write(f'  Inserted {len(STUB_SKILLS)} skill rows')

        # Currency
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO character_currency (id, platinum, gold, silver, copper) "
                "VALUES (%s, %s, %s, %s, %s)",
                [char_id, 500, 0, 0, 0],
            )
        self.stdout.write('  Inserted currency row')

        # Default Magelo permissions (wishlist public, inventory hidden)
        CharacterPermissions.get_or_create_permissions(name)
        self.stdout.write('  Created CharacterPermissions')

        self.stdout.write(self.style.SUCCESS(
            f'\nStub character "{name}" ready.\n'
            f'  Profile: /magelo/view/{name}\n'
            f'  Wishlist: /magelo/wishlist/{name}/'
        ))
