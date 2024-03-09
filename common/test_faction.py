from django.test import TestCase
from common.faction import FactionMods
from common.faction import FactionValue
from common.faction import calculate_faction_value
from common.faction import faction_value_to_string


class FactionTestCase(TestCase):

    def setUp(self) -> None:
        pass

    def test_faction_value_enum(self):
        self.assertEqual(FactionValue.FACTION_MAX_ALLY.value, 0)
        self.assertEqual(FactionValue.FACTION_ALLY.value, 1)
        self.assertEqual(FactionValue.FACTION_WARMLY.value, 2)
        self.assertEqual(FactionValue.FACTION_KINDLY.value, 3)
        self.assertEqual(FactionValue.FACTION_AMIABLY.value, 4)
        self.assertEqual(FactionValue.FACTION_INDIFFERENTLY.value, 5)
        self.assertEqual(FactionValue.FACTION_APPREHENSIVELY.value, 6)
        self.assertEqual(FactionValue.FACTION_DUBIOUSLY.value, 7)
        self.assertEqual(FactionValue.FACTION_THREATENINGLY.value, 8)
        self.assertEqual(FactionValue.FACTION_SCOWLS.value, 9)
        self.assertEqual(FactionValue.FACTION_MAX_SCOWLS.value, 10)

    def test_faction_value_to_string(self):
        self.assertEqual(faction_value_to_string(FactionValue.FACTION_MAX_ALLY), "Max Ally")
        self.assertEqual(faction_value_to_string(FactionValue.FACTION_ALLY), "Ally")
        self.assertEqual(faction_value_to_string(FactionValue.FACTION_WARMLY), "Warmly")
        self.assertEqual(faction_value_to_string(FactionValue.FACTION_KINDLY), "Kindly")
        self.assertEqual(faction_value_to_string(FactionValue.FACTION_AMIABLY), "Amiably")
        self.assertEqual(faction_value_to_string(FactionValue.FACTION_INDIFFERENTLY), "Indifferently")
        self.assertEqual(faction_value_to_string(FactionValue.FACTION_APPREHENSIVELY), "Apprehensively")
        self.assertEqual(faction_value_to_string(FactionValue.FACTION_DUBIOUSLY), "Dubiously")
        self.assertEqual(faction_value_to_string(FactionValue.FACTION_THREATENINGLY), "Threateningly")
        self.assertEqual(faction_value_to_string(FactionValue.FACTION_SCOWLS), "Scowls")

    def test_calculate_faction_value(self):
        # FactionValue.FACTION_MAX_ALLY is any value >= 2000
        fmod = FactionMods(base_mod=0, class_mod=0, race_mod=0, deity_mod=0)
        self.assertEqual(calculate_faction_value(fmod, 2005), FactionValue.FACTION_MAX_ALLY)
        self.assertEqual(calculate_faction_value(fmod, 2000), FactionValue.FACTION_MAX_ALLY)
        self.assertNotEquals(calculate_faction_value(fmod, 1999), FactionValue.FACTION_MAX_ALLY)

        # FactionValue.INDIFFERENTLY is the range of 0 <= character_value <= 99
        self.assertNotEquals(calculate_faction_value(fmod, -1), FactionValue.FACTION_INDIFFERENTLY)
        self.assertEqual(calculate_faction_value(fmod, 0), FactionValue.FACTION_INDIFFERENTLY)
        self.assertEqual(calculate_faction_value(fmod, 99), FactionValue.FACTION_INDIFFERENTLY)
        self.assertNotEquals(calculate_faction_value(fmod, 100), FactionValue.FACTION_INDIFFERENTLY)

        # FactionValue.FACTION_SCOWLS is the range of -1999 <= character_value <= -751
        fmod = FactionMods(base_mod=0, class_mod=0, race_mod=0, deity_mod=0)
        self.assertNotEquals(calculate_faction_value(fmod, -750), FactionValue.FACTION_SCOWLS)
        self.assertEqual(calculate_faction_value(fmod, -751), FactionValue.FACTION_SCOWLS)
        self.assertEqual(calculate_faction_value(fmod, -1999), FactionValue.FACTION_SCOWLS)
        self.assertNotEquals(calculate_faction_value(fmod, -2000), FactionValue.FACTION_SCOWLS)

        # FactionValue.FACTION_MAX_SCOWLS is any value <= -2000
        fmod = FactionMods(base_mod=0, class_mod=0, race_mod=0, deity_mod=0)
        self.assertEqual(calculate_faction_value(fmod, -2000), FactionValue.FACTION_MAX_SCOWLS)
        self.assertEqual(calculate_faction_value(fmod, -2005), FactionValue.FACTION_MAX_SCOWLS)
        self.assertEqual(calculate_faction_value(fmod, -3005), FactionValue.FACTION_MAX_SCOWLS)
