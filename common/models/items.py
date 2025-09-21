from django.db import models


class Items(models.Model):
    """
    This model maps to the items table in the database.
    """

    def __str__(self):
        return str(self.id)

    id = models.IntegerField(primary_key=True, null=False, default=0)
    idfile = models.CharField(null=False, max_length=30)
    minstatus = models.SmallIntegerField(null=False, default=0)
    Name = models.CharField(max_length=64, null=False, default=0)
    aagi = models.IntegerField(null=False, default=0)
    acha = models.IntegerField(null=False, default=0)
    adex = models.IntegerField(null=False, default=0)
    aint = models.IntegerField(null=False, default=0)
    asta = models.IntegerField(null=False, default=0)
    astr = models.IntegerField(null=False, default=0)
    awis = models.IntegerField(null=False, default=0)
    hp = models.IntegerField(null=False, default=0)
    mana = models.IntegerField(null=False, default=0)
    fr = models.IntegerField(null=False, default=0)
    dr = models.IntegerField(null=False, default=0)
    cr = models.IntegerField(null=False, default=0)
    mr = models.IntegerField(null=False, default=0)
    pr = models.IntegerField(null=False, default=0)
    max_charges = models.IntegerField(null=False, default=0, db_column='maxcharges')
    scroll_effect = models.IntegerField(null=False, default=0, db_column='scrolleffect')
    scroll_type = models.IntegerField(null=False, default=0, db_column='scrolltype')
    source = models.CharField(max_length=20, null=False)
    icon = models.IntegerField(null=False, default=0)
    price = models.IntegerField(null=False, default=0)
    no_drop = models.IntegerField(null=False, default=0, db_column='nodrop')
    no_rent = models.IntegerField(null=False, default=0, db_column='norent')
    lore = models.CharField(max_length=80, null=False)
    magic = models.IntegerField(null=False, default=0)
    slots = models.IntegerField(null=False, default=0)
    ac = models.IntegerField(null=False, default=0)
    stackable = models.IntegerField(null=False, default=0)
    click_effect = models.IntegerField(null=False, default=0, db_column='clickeffect')
    click_type = models.IntegerField(null=False, default=0, db_column='clicktype')
    worn_effect = models.IntegerField(null=False, default=0, db_column='worneffect')
    worn_type = models.IntegerField(null=False, default=0, db_column='worntype')
    worn_level = models.IntegerField(null=False, default=0, db_column='wornlevel')
    worn_level2 = models.IntegerField(null=False, default=0, db_column='wornlevel2')
    proc_type = models.IntegerField(null=False, default=0, db_column='proctype')
    proc_level = models.IntegerField(null=False, default=0, db_column='proclevel')
    proc_effect = models.IntegerField(null=False, default=0, db_column='proceffect')
    cast_time = models.IntegerField(null=False, default=0, db_column='casttime')
    focus_effect = models.IntegerField(null=False, default=0, db_column='focuseffect')
    focus_type = models.IntegerField(null=False, default=0, db_column='focustype')
    focus_level = models.IntegerField(null=False, default=0, db_column='focuslevel')
    focus_level2 = models.IntegerField(null=False, default=0, db_column='focuslevel2')
    skill_mod_type = models.IntegerField(null=False, default=0, db_column='skillmodtype')
    skill_mod_value = models.IntegerField(null=False, default=0, db_column='skillmodvalue')
    proc_level2 = models.IntegerField(null=False, default=0, db_column='proclevel2')
    cast_time2 = models.IntegerField(null=False, default=0, db_column='casttime_')
    click_level = models.IntegerField(null=False, default=0, db_column='clicklevel')
    click_level2 = models.IntegerField(null=False, default=0, db_column='clicklevel2')
    scroll_level = models.IntegerField(null=False, default=0, db_column='scrolllevel')
    scroll_level2 = models.IntegerField(null=False, default=0, db_column='scrolllevel2')
    material = models.IntegerField(null=False, default=0)
    color = models.IntegerField(null=False, default=0)
    light = models.IntegerField(null=False, default=0)
    filename = models.CharField(max_length=32, null=False)
    book = models.IntegerField(null=False, default=0)
    booktype = models.IntegerField(null=False, default=0)
    tradeskills = models.IntegerField(null=False, default=0)
    stacksize = models.IntegerField(null=False, default=0)
    recast_delay = models.IntegerField(null=False, default=0, db_column='recastdelay')
    recast_type = models.IntegerField(null=False, default=0, db_column='recasttype')
    proc_rate = models.IntegerField(null=False, default=0, db_column='procrate')
    range = models.IntegerField(null=False, default=0)
    req_level = models.IntegerField(null=False, default=0, db_column='reqlevel')
    rec_skill = models.IntegerField(null=False, default=0, db_column='recskill')
    item_class = models.IntegerField(null=False, default=0, db_column='itemclass')
    sell_rate = models.FloatField(null=False, default=0, db_column='sellrate')
    fv_nodrop = models.IntegerField(null=False, default=0, db_column='fvnodrop')
    bane_dmg_amt = models.IntegerField(null=False, default=0, db_column='banedmgamt')
    bane_dmg_body = models.IntegerField(null=False, default=0, db_column='banedmgbody')
    bane_dmg_race = models.IntegerField(null=False, default=0, db_column='banedmgrace')
    elem_dmg_type = models.IntegerField(null=False, default=0, db_column='elemdmgtype')
    elem_dmg_amt = models.IntegerField(null=False, default=0, db_column='elemdmgamt')
    faction_mod1 = models.IntegerField(null=False, default=0, db_column='factionmod1')
    faction_mod2 = models.IntegerField(null=False, default=0, db_column='factionmod2')
    faction_mod3 = models.IntegerField(null=False, default=0, db_column='factionmod3')
    faction_mod4 = models.IntegerField(null=False, default=0, db_column='factionmod4')
    faction_amt1 = models.IntegerField(null=False, default=0, db_column='factionamt1')
    faction_amt2 = models.IntegerField(null=False, default=0, db_column='factionamt2')
    faction_amt3 = models.IntegerField(null=False, default=0, db_column='factionamt3')
    faction_amt4 = models.IntegerField(null=False, default=0, db_column='factionamt4')
    bard_type = models.IntegerField(null=False, default=0, db_column='bardtype')
    bard_value = models.IntegerField(null=False, default=0, db_column='bardvalue')
    bard_effect = models.SmallIntegerField(null=False, default=0, db_column='bardeffect')
    bard_effect_type = models.SmallIntegerField(null=False, default=0, db_column='bardeffecttype')
    bard_level = models.SmallIntegerField(null=False, default=0, db_column='bardlevel')
    bard_level2 = models.SmallIntegerField(null=False, default=0, db_column='bardlevel2')
    updated = models.DateTimeField(null=False, default='0000-00-00 00:00:00')
    created = models.CharField(max_length=64, null=False)
    comment = models.CharField(max_length=255, null=False)
    lore_file = models.CharField(max_length=32, null=False, db_column='lorefile')
    quest_item_flag = models.IntegerField(null=False, default=0, db_column='questitemflag')
    gm_flag = models.IntegerField(null=False, default=0, db_column='gmflag')
    soul_bound = models.IntegerField(null=False, default=0, db_column='soulbound')
    weight = models.IntegerField(null=False, default=0)
    size = models.IntegerField(null=False, default=0)
    item_type = models.IntegerField(null=False, default=0, db_column='itemtype')
    delay = models.IntegerField(null=False, default=0)
    classes = models.IntegerField(null=False, default=0)
    races = models.IntegerField(null=False, default=0)
    deity = models.IntegerField(null=False, default=0)
    damage = models.IntegerField(null=False, default=0)
    rec_level = models.IntegerField(null=False, default=0, db_column='reclevel')
    bag_size = models.IntegerField(null=False, default=0, db_column='bagsize')
    bag_slots = models.IntegerField(null=False, default=0, db_column='bagslots')
    bag_type = models.IntegerField(null=False, default=0, db_column='bagtype')
    bag_wr = models.IntegerField(null=False, default=0, db_column='bagwr')

    class Meta:
        db_table = 'items'
        managed = False

    def get_slot_display(self):
        """Convert slots bitfield to readable format"""
        if not self.slots:
            return ""

        slot_checks = [
            ([2, 16], "EARS"),
            ([4], "HEAD"),
            ([8], "FACE"),
            ([32], "NECK"),
            ([64], "SHOULDER"),
            ([128], "ARMS"),
            ([256], "BACK"),
            ([512, 1024], "WRIST"),
            ([2048], "RANGE"),
            ([4096], "HANDS"),
            ([8192], "PRIMARY"),
            ([16384], "SECONDARY"),
            ([32768, 65536], "FINGERS"),
            ([131072], "CHEST"),
            ([262144], "LEGS"),
            ([524288], "FEET"),
            ([1048576], "WAIST"),
            ([2097152], "POWERSOURCE"),
            ([4194304], "AMMO"),
        ]

        slots_available = [
            slot_name for bits, slot_name in slot_checks
            if any(self.slots & bit for bit in bits)
        ]

        return " ".join(slots_available)

    def get_item_type_display(self):
        """Convert item type to readable format"""
        type_mapping = {
            0: "1H Slashing", 1: "2H Slashing", 2: "1H Piercing",
            3: "1H Blunt", 4: "2H Blunt", 5: "Archery", 6: "Shield",
            7: "Armor", 8: "Misc", 9: "Lockpicks", 10: "Unused",
            11: "1H Piercing", 12: "Unused", 13: "Unused", 14: "Unused",
            15: "Unused", 16: "Unused", 17: "Unused", 18: "Unused",
            19: "Unused", 20: "Thrown", 21: "Bow", 22: "Unused",
            23: "Key", 24: "Unused", 25: "Unused", 26: "Unused",
            27: "Unused", 28: "Unused", 29: "Unused", 30: "Unused",
            31: "Unused", 32: "Unused", 33: "Unused", 34: "Unused",
            35: "2H Piercing"
        }
        return type_mapping.get(self.item_type, f"Unknown ({self.item_type})")

    def get_class_restrictions_display(self):
        """Convert classes bitfield to readable format"""
        if not self.classes or self.classes == 32767:  # 32767 = all classes
            return ""

        class_mapping = {
            1: "WAR", 2: "CLR", 4: "PAL", 8: "RNG", 16: "SHD",
            32: "DRU", 64: "MNK", 128: "BRD", 256: "ROG", 512: "SHM",
            1024: "NEC", 2048: "WIZ", 4096: "MAG", 8192: "ENC", 16384: "BST"
        }

        classes = []
        for bit_value, class_name in class_mapping.items():
            if self.classes & bit_value:
                classes.append(class_name)

        return " ".join(classes)

    def get_race_restrictions_display(self):
        """Convert races bitfield to readable format"""
        if not self.races or self.races == 16383:  # All races
            return ""

        race_mapping = {
            1: "HUM", 2: "BAR", 4: "ERU", 8: "ELF", 16: "HIE", 32: "DEF",
            64: "HEF", 128: "DWF", 256: "TRL", 512: "OGR", 1024: "HFL",
            2048: "GNM", 4096: "IKS", 8192: "VAH"
        }

        races = []
        for bit_value, race_name in race_mapping.items():
            if self.races & bit_value:
                races.append(race_name)

        return " ".join(races)

    def get_size_display(self):
        """Convert size to readable format"""
        size_mapping = {0: "TINY", 1: "SMALL", 2: "MEDIUM", 3: "LARGE", 4: "GIANT"}
        return size_mapping.get(self.size, "UNKNOWN")

    def get_weight_display(self):
        """Convert weight to readable format with decimal handling"""
        if self.weight == 0:
            return "0.0"
        elif self.weight < 10:
            return f"0.{self.weight}"
        else:
            return f"{self.weight // 10}.{self.weight % 10}"

    def format_stat_value(self, value):
        """Format stat values with proper +/- prefix"""
        if value > 0:
            return f"+{value}"
        return str(value)

    def generate_og_description(self, effect_name=None, focus_effect_name=None):
        """Generate Open Graph description for Discord/social media"""
        lines = []

        # Item flags row
        flags = []
        if self.magic:
            flags.append("MAGIC ITEM")
        if self.no_rent == 0:
            flags.append("NO RENT")
        if self.lore and self.lore.startswith('*'):
            flags.append("LORE ITEM")
        if self.no_drop == 0:
            flags.append("NODROP")

        if flags:
            lines.append(" ".join(flags))

        # Slot information
        slot_display = self.get_slot_display()
        if slot_display:
            lines.append(f"Slot: {slot_display}")

        # Skill and delay - only for weapons
        skill_delay_parts = []
        weapon_types = [0, 1, 2, 3, 4, 5, 35]  # Various weapon types
        if self.item_type in weapon_types:
            type_display = self.get_item_type_display()
            if "Unknown" not in type_display:
                skill_delay_parts.append(f"Skill: {type_display}")
        if self.delay:
            skill_delay_parts.append(f"Atk Delay: {self.delay}")

        if skill_delay_parts:
            lines.append(" ".join(skill_delay_parts))

        # Damage
        if self.damage:
            lines.append(f"DMG: {self.damage}")

        # Charges
        if self.max_charges > 0:
            lines.append(f"Charges: {self.max_charges}")

        # AC
        if self.ac:
            lines.append(f"AC: {self.ac}")

        # Stats
        stats = []
        stat_fields = [
            (self.astr, 'STR'), (self.adex, 'DEX'), (self.asta, 'STA'),
            (self.acha, 'CHA'), (self.awis, 'WIS'), (self.aint, 'INT'),
            (self.aagi, 'AGI'), (self.hp, 'HP')
        ]

        for value, display in stat_fields:
            if value:
                stats.append(f"{display}: {self.format_stat_value(value)}")

        if self.mana:
            stats.append(f"MANA: +{self.mana}")

        if stats:
            lines.append(" ".join(stats))

        # Resistances
        resists = []
        resist_fields = [
            (self.fr, 'SV FIRE'), (self.dr, 'SV DISEASE'), (self.cr, 'SV COLD'),
            (self.mr, 'SV MAGIC'), (self.pr, 'SV POISON')
        ]

        for value, display in resist_fields:
            if value:
                resists.append(f"{display}: +{value}")

        if resists:
            lines.append(" ".join(resists))

        # Focus effects and skill modifiers
        focus_mods = []

        # Skill modifiers
        if self.skill_mod_value and self.skill_mod_value != 0:
            skill_name = self.get_skill_mod_display()
            focus_mods.append(f"Skill Mod: {skill_name} +{self.skill_mod_value}%")

        # Focus effects (these need separate effect name lookup)
        if self.focus_effect and self.focus_effect > 0:
            if focus_effect_name:
                focus_mods.append(f"Focus: {focus_effect_name}")
            else:
                focus_mods.append(f"Focus Effect: {self.focus_effect}")

        if focus_mods:
            lines.extend(focus_mods)

        # Effects (if stackable == 3 means spell effect)
        if self.stackable == 3 and effect_name:
            effects = []

            # Click effects
            if self.click_type in [1, 3, 4, 5]:
                effect_parts = [f"Effect: {effect_name}"]
                if self.click_type == 1:
                    effect_parts.append("(Any Slot,")
                elif self.click_type == 4:
                    effect_parts.append("(Must Equip,")

                cast_time = "Instant" if self.cast_time in [0, -1] else f"{self.cast_time / 1000:.1f} sec"
                effect_parts.append(f"Casting Time: {cast_time})")
                effects.append(" ".join(effect_parts))

            # Worn effects
            if self.worn_type == 2:
                worn_effect = f"Effect: {effect_name} (Worn)"
                if self.worn_effect == 998 and self.worn_level:
                    worn_effect += f" ({self.worn_level + 1}%)"
                effects.append(worn_effect)

            # Proc effects
            if self.proc_type == 0 and self.proc_effect > 0:
                cast_time = "Instant" if self.cast_time == 0 else f"{self.cast_time / 1000:.1f} sec"
                effects.append(f"Effect: {effect_name} (Combat, Casting Time: {cast_time}) at Level {self.proc_level}")

            if effects:
                lines.extend(effects)

        # Recommended level
        if self.rec_level:
            lines.append(f"Recommended level of {self.rec_level}.")

        # Weight and size
        weight_parts = [f"WT: {self.get_weight_display()}"]

        if self.bag_type:
            if self.bag_wr:
                weight_parts.append(f"Weight Reduction: {self.bag_wr}%")
            weight_parts.append(f"Capacity: {self.bag_slots}")
            weight_parts.append(f"Size Capacity: {self.get_size_display()}")
        else:
            weight_parts.append(f"Size: {self.get_size_display()}")

        lines.append(" ".join(weight_parts))

        # Classes
        class_display = self.get_class_restrictions_display()
        if class_display:
            lines.append(f"Class: {class_display}")

        # Races
        race_display = self.get_race_restrictions_display()
        if race_display:
            lines.append(f"Race: {race_display}")

        return "\n".join(lines)

    def get_skill_mod_display(self):
        """Convert skill_mod_type to readable format"""
        skill_mapping = {
            0: "1H Blunt", 1: "1H Slashing", 2: "2H Blunt", 3: "2H Slashing",
            4: "Abjuration", 5: "Alteration", 6: "Apply Poison", 7: "Archery",
            8: "Backstab", 9: "Bind Wound", 10: "Bash", 11: "Block",
            12: "Brass Instruments", 13: "Channeling", 14: "Conjuration",
            15: "Defense", 16: "Disarm", 17: "Disarm Traps", 18: "Divination",
            19: "Dodge", 20: "Double Attack", 21: "Dragon Punch", 22: "Dual Wield",
            23: "Eagle Strike", 24: "Evocation", 25: "Feign Death", 26: "Flying Kick",
            27: "Forage", 28: "Hand to Hand", 29: "Hide", 30: "Kick",
            31: "Meditate", 32: "Mend", 33: "Offense", 34: "Parry",
            35: "Pick Lock", 36: "1H Piercing", 37: "Riposte", 38: "Round Kick",
            39: "Safe Fall", 40: "Sense Heading", 41: "Singing", 42: "Sneak",
            43: "Specialize Abjure", 44: "Specialize Alteration", 45: "Specialize Conjuration",
            46: "Specialize Divination", 47: "Specialize Evocation", 48: "Pick Pockets",
            49: "Stringed Instruments", 50: "Swimming", 51: "Throwing", 52: "Tiger Claw",
            53: "Tracking", 54: "Wind Instruments", 55: "Fishing", 56: "Make Poison",
            57: "Tinkering", 58: "Research", 59: "Alchemy", 60: "Baking",
            61: "Tailoring", 62: "Sense Traps", 63: "Blacksmithing", 64: "Fletching",
            65: "Brewing", 66: "Alcohol Tolerance", 67: "Begging", 68: "Jewelrymaking",
            69: "Pottery", 70: "Percussion Instruments", 71: "Intimidation",
            72: "Berserking", 73: "Taunt"
        }
        return skill_mapping.get(self.skill_mod_type, f"Unknown Skill ({self.skill_mod_type})")

    def get_clean_name(self):
        """Remove underscores and prepended # from item names"""
        if self.Name:
            cleaned = self.Name.replace('_', ' ')
            return cleaned.replace('#', '')
        return self.Name


class DiscoveredItems(models.Model):
    """
    This model maps to the discovered_items table in the database.
    """
    item_id = models.OneToOneField(Items, on_delete=models.DO_NOTHING, primary_key=True, db_column='item_id')
    char_name = models.CharField(max_length=64, null=False)
    discovered_date = models.IntegerField(null=False, default=0)
    account_status = models.IntegerField(null=False, default=0)

    class Meta:
        db_table = 'discovered_items'
        managed = False
