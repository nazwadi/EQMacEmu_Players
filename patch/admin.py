from django.contrib import admin

from .models import PatchMessage
from .models import Comment

class PatchMessageAdmin(admin.ModelAdmin):
    list_display = ("title", "body_plaintext",)
    prepopulated_fields = {"slug": ("title", "patch_number_this_date")}

class CommentAdmin(admin.ModelAdmin):
    list_display = ('username', 'body', 'patch_message', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('username', 'email', 'body')
    actions = ['approve_comments']

    @staticmethod
    def approve_comments(self, request, queryset):
        queryset.update(active=True)

admin.site.register(PatchMessage, PatchMessageAdmin)
admin.site.register(Comment, CommentAdmin)
