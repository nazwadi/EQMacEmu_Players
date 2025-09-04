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

        slot_mapping = {
            1: "CHARM", 2: "EAR", 4: "HEAD", 8: "FACE", 16: "NECK",
            32: "SHOULDER", 64: "ARMS", 128: "BACK", 256: "WRIST",
            512: "HANDS", 1024: "SHIELD", 2048: "BELT", 4096: "LEGS",
            8192: "FEET", 16384: "FINGER", 32768: "PRIMARY", 65536: "SECONDARY"
        }

        slots = []
        for bit_value, slot_name in slot_mapping.items():
            if self.slots & bit_value:
                slots.append(slot_name)

        return " ".join(slots)

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

    def generate_og_description(self):
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

        # Skill and delay
        skill_delay_parts = []
        if self.item_type >= 0:
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

