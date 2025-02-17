from django.contrib import admin
from .models import CharacterPermissions


@admin.register(CharacterPermissions)
class CharacterPermissionsAdmin(admin.ModelAdmin):
    list_display = ('character_name', 'inventory', 'bags', 'bank', 'coin_inventory', 'coin_bank', 'updated_at', 'created_at')
    list_filter = ('inventory', 'bags', 'bank', 'coin_inventory', 'coin_bank')
    search_fields = ('character_name',)
    readonly_fields = ('created_at', 'updated_at')

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of permission objects - they should only be toggled
        return False
