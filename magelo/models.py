from django.db import models

class CharacterPermissions(models.Model):
    character_name = models.CharField(max_length=64, unique=True)
    inventory = models.BooleanField(default=False)
    bags = models.BooleanField(default=False)
    bank = models.BooleanField(default=False)
    coin_inventory = models.BooleanField(default=False)
    coin_bank = models.BooleanField(default=False)

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
