from django.contrib import admin

from .models import PatchMessage, Comment, PatchTag


class PatchTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class PatchMessageAdmin(admin.ModelAdmin):
    list_display = ("title", "patch_date", "patch_type", "expansion", "markdown_edited", "short_description")
    list_filter = ("patch_type", "expansion", "markdown_edited", "patch_year", "tags")
    search_fields = ["title", "body_plaintext"]
    prepopulated_fields = {"slug": ("title", "patch_number_this_date")}
    readonly_fields = ("markdown_edited",)
    filter_horizontal = ("tags",)

    def save_model(self, request, obj, form, change):
        if 'body_markdown' in form.changed_data:
            obj.markdown_edited = True
        super().save_model(request, obj, form, change)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('username', 'body', 'patch_message', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('username', 'body')
    actions = ['approve_comments']

    @staticmethod
    def approve_comments(self, request, queryset):
        queryset.update(active=True)


admin.site.register(PatchMessage, PatchMessageAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(PatchTag, PatchTagAdmin)
