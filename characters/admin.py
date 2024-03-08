from django.contrib import admin

# Register your models here.
from .models import Characters


class CharactersAdmin(admin.ModelAdmin):
    search_fields = ["id", "name"]
    list_display = ["id", "name", "class_name", "level"]
    list_filter = ["name"]


admin.site.register(Characters, CharactersAdmin)
