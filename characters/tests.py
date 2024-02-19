from django.test import TestCase
from characters.models import Characters
from characters.models import CharacterKeyring


class CharacterKeyringTest(TestCase):
    def setUp(self):
        c = Characters.objects.create()
        CharacterKeyring.objects.create(id=c, item_id='2803')

    def test_character_keyring(self):
        value = CharacterKeyring.objects.get(id='1')
        self.assertEqual(value.item_id, '2803')

