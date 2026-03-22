from django.contrib import admin

from items.models import BISEntry, BISRevision
from common.constants import PLAYER_CLASSES


class ClassIdFilter(admin.SimpleListFilter):
    title = 'class'
    parameter_name = 'class_id'

    def lookups(self, request, model_admin):
        return [(cid, name) for cid, name in PLAYER_CLASSES.items() if cid != 0]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(class_id=self.value())
        return queryset


@admin.register(BISEntry)
class BISEntryAdmin(admin.ModelAdmin):
    list_display = ['get_class_name', 'expansion', 'slot', 'rank', 'item_name', 'item_id']
    list_filter = [ClassIdFilter, 'expansion']
    search_fields = ['item_name', 'slot']
    ordering = ['class_id', 'expansion', 'slot', 'rank']

    @admin.display(description='Class', ordering='class_id')
    def get_class_name(self, obj):
        return PLAYER_CLASSES.get(obj.class_id, str(obj.class_id))


@admin.register(BISRevision)
class BISRevisionAdmin(admin.ModelAdmin):
    list_display = ['changed_at', 'changed_by', 'get_class_name', 'expansion', 'slot', 'action', 'item_name', 'edit_summary']
    list_filter = ['action', 'expansion', ClassIdFilter]
    search_fields = ['item_name', 'changed_by__username']
    ordering = ['-changed_at']
    readonly_fields = ['changed_at']

    @admin.display(description='Class', ordering='class_id')
    def get_class_name(self, obj):
        return PLAYER_CLASSES.get(obj.class_id, str(obj.class_id))
