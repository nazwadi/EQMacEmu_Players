from django.contrib import admin

# Register your models here.
from common.models.characters import Characters
from .templatetags.data_utilities import player_class  # Import your filter function


class CharactersAdmin(admin.ModelAdmin):
    search_fields = ["id", "name"]
    list_display = ["id", "name", "get_class_name", "level"]
    list_filter = ["name"]

    def get_class_name(self, obj):
        """Apply the player_class filter to the class_name field"""
        return player_class(obj.class_name)

    get_class_name.short_description = 'Class'  # Sets the column header in the admin
    get_class_name.admin_order_field = 'class_name'  # Tells Django to sort by class_name when this column is clicked


admin.site.register(Characters, CharactersAdmin)
