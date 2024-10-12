from django.test import TestCase
from .se_utils import describe_se_ac

class SpellTests(TestCase):
    def test_ACSpell(self):
        description = describe_se_ac('AC', -103, -115, 53, 65)
        self.assertEqual(description, "Decrease AC for Cloth Casters by 40 (L53) to 44 (L65), Everyone else by 29 (L53) to 33 (L65)")