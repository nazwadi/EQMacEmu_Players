from django.contrib import admin

# Register your models here.
from .models import Characters


class CharactersAdmin(admin.ModelAdmin):
    list_filter = ["name"]


admin.site.register(Characters, CharactersAdmin)
