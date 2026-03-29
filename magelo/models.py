from django.db import models

class CharacterPermissions(models.Model):
    character_name = models.CharField(max_length=64, unique=True)
    inventory = models.BooleanField(default=False)
    bags = models.BooleanField(default=False)
    bank = models.BooleanField(default=False)
    coin_inventory = models.BooleanField(default=False)
    coin_bank = models.BooleanField(default=False)
    wishlist_public = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Character Permissions'
        verbose_name_plural = 'Character Permissions'

    def __str__(self):
        return f"Permissions for {self.character_name}"

    @classmethod
    def get_or_create_permissions(cls, character_name):
        """Get or create permissions for a user."""
        permissions, created = cls.objects.get_or_create(
            character_name=character_name
        )
        return permissions


class WishlistEntry(models.Model):
    """
    A single item on a character's gear wishlist.

    item_id and item_name reference the game database Items table by ID.
    No ForeignKey is used because Items lives in a separate database.
    item_name is denormalized to avoid cross-database joins on list pages.
    """
    character_name = models.CharField(max_length=64, db_index=True)
    item_id = models.IntegerField()
    item_name = models.CharField(max_length=200)
    priority = models.PositiveSmallIntegerField(default=0)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('character_name', 'item_id')
        ordering = ['priority', 'created_at']
        verbose_name = 'Wishlist Entry'
        verbose_name_plural = 'Wishlist Entries'

    def __str__(self):
        return f"{self.character_name}'s wishlist: {self.item_name}"
