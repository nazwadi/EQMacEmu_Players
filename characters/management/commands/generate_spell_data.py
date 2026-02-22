import json
import characters.templatetags.data_utilities as du
from pathlib import Path
from common.models.items import Items
from common.models.spells import SpellsNew
from django.db.models import F
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generates per-class spell data JSON files for the characters app'

    def add_arguments(self, parser):
        # optional: add CLI arguments here
        pass

    def handle(self, *args, **options):
        generate_spell_list(class_id=1)
        generate_spell_list(class_id=2)
        generate_spell_list(class_id=3)
        generate_spell_list(class_id=4)
        generate_spell_list(class_id=5)
        generate_spell_list(class_id=6)
        generate_spell_list(class_id=7)
        generate_spell_list(class_id=8)
        generate_spell_list(class_id=9)
        generate_spell_list(class_id=10)
        generate_spell_list(class_id=11)
        generate_spell_list(class_id=12)
        generate_spell_list(class_id=13)
        generate_spell_list(class_id=14)
        generate_spell_list(class_id=15)
        self.stdout.write('Done.')


def generate_spell_list(class_id: int):
    spell_list = None
    max_level = 60
    match class_id:
        case 1:  # Warrior - might remove, but disciplines are also spells
            spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                   classes1__gte=1,
                                                   classes1__lte=max_level)
                          .annotate(level=F('classes1'))
                          .order_by('classes1', 'name'))
        case 2:  # Cleric
            spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                   classes2__gte=1,
                                                   classes2__lte=max_level)
                          .annotate(level=F('classes2'))
                          .order_by('classes2', 'name'))
        case 3:  # Paladin
            spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                   classes3__gte=1,
                                                   classes3__lte=max_level)
                          .annotate(level=F('classes3'))
                          .order_by('classes3', 'name'))
        case 4:  # Ranger
            spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                   classes4__gte=1,
                                                   classes4__lte=max_level)
                          .annotate(level=F('classes4'))
                          .order_by('classes4', 'name'))
        case 5:  # Shadowknight
            spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                   classes5__gte=1,
                                                   classes5__lte=max_level)
                          .annotate(level=F('classes5'))
                          .order_by('classes5', 'name'))
        case 6:  # Druid
            spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                   classes6__gte=1,
                                                   classes6__lte=max_level)
                          .annotate(level=F('classes6'))
                          .order_by('classes6', 'name'))
        case 7:  # Monk
            spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                   classes7__gte=1,
                                                   classes7__lte=max_level)
                          .annotate(level=F('classes7'))
                          .order_by('classes7', 'name'))
        case 8:  # Bard
            spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                   classes8__gte=1,
                                                   classes8__lte=max_level)
                          .annotate(level=F('classes8'))
                          .order_by('classes8', 'name'))
        case 9:  # Rogue
            spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                   classes9__gte=1,
                                                   classes9__lte=max_level)
                          .annotate(level=F('classes9'))
                          .order_by('classes9', 'name'))
        case 10:  # Shaman
            spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                   classes10__gte=1,
                                                   classes10__lte=max_level)
                          .annotate(level=F('classes10'))
                          .order_by('classes10', 'name'))
        case 11:  # Necromancer
            spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                   classes11__gte=1,
                                                   classes11__lte=max_level)
                          .annotate(level=F('classes11'))
                          .order_by('classes11', 'name'))
        case 12:  # Wizard
            spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                   classes12__gte=1,
                                                   classes12__lte=max_level)
                          .annotate(level=F('classes12'))
                          .order_by('classes12', 'name'))
        case 13:  # Magician
            spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                   classes13__gte=1,
                                                   classes13__lte=max_level)
                          .annotate(level=F('classes13'))
                          .order_by('classes13', 'name'))
        case 14:  # Enchanter
            spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                   classes14__gte=1,
                                                   classes14__lte=max_level)
                          .annotate(level=F('classes14'))
                          .order_by('classes14', 'name'))
        case 15:  # Beastlord
            spell_list = (SpellsNew.objects.filter(not_player_spell=0,
                                                   classes15__gte=1,
                                                   classes15__lte=max_level)
                          .annotate(level=F('classes15'))
                          .order_by('classes15', 'name'))

    output = dict()
    for spell in spell_list:
        scrolls = Items.objects.filter(scroll_effect=spell.id, scroll_type=7)
        if spell is not None and scrolls is not None:
            spell_data = {
                "name": spell.name,
                "spell_id": spell.id,
                "lucy": "https://lucy.allakhazam.com/spell.html?id=" + str(spell.id),
                "alkabor_lucy": "https://lucy.alkabor.com/spell_" + str(spell.id) + ".html",
                "level": spell.level,
                "effects": "",
                "classes1": spell.classes1,
                "classes2": spell.classes2,
                "classes3": spell.classes3,
                "classes4": spell.classes4,
                "classes5": spell.classes5,
                "classes6": spell.classes6,
                "classes7": spell.classes7,
                "classes8": spell.classes8,
                "classes9": spell.classes9,
                "classes10": spell.classes10,
                "classes11": spell.classes11,
                "classes12": spell.classes12,
                "classes13": spell.classes13,
                "classes14": spell.classes14,
                "classes15": spell.classes15,
                "mana": spell.mana,
                "skill": du.player_skill(spell.skill),
                "target_type": du.spell_target_type(spell.target_type),
                "scrolls": [(scroll.id, scroll.Name) for scroll in scrolls],
                "expansion": 0 if spell.level <= 49 else 1,  # Starting point
                "custom_icon": spell.custom_icon
            }
            if spell.level in output:
                output[spell.level].append(spell_data)
            else:
                output[spell.level] = [spell_data]
    output_path = Path(__file__).resolve().parent.parent.parent.parent / 'static' / 'spell_data'
    with open(output_path / f'{class_id}.json', 'w') as json_file:
        json.dump(output, json_file, indent=4)

