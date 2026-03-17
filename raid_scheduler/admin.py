from django import forms
from django.contrib import admin
from django.utils.html import format_html

from .models import GMOverrideLog, RaidEvent, RaidSignup, RaidTarget
from .conflicts import check_conflicts


class RaidSignupInline(admin.TabularInline):
    model = RaidSignup
    extra = 0
    fields = ('member', 'display_name', 'status', 'note')
    autocomplete_fields = ()


class GMOverrideLogInline(admin.TabularInline):
    model = GMOverrideLog
    extra = 0
    readonly_fields = ('overridden_by', 'reason', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class RaidEventAdminForm(forms.ModelForm):
    """Adds a non-model "GM override reason" field for audit logging."""
    gm_override_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2}),
        label='GM override reason',
        help_text=(
            'Required when scheduling past a hard conflict. '
            'Leave blank if no conflict exists.'
        ),
    )

    class Meta:
        model = RaidEvent
        fields = '__all__'


@admin.register(RaidEvent)
class RaidEventAdmin(admin.ModelAdmin):
    form = RaidEventAdminForm
    list_display = ('title', 'date', 'start_time', 'circuit_display', 'is_public', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'is_public', 'date', 'targets')
    search_fields = ('title', 'targets__name', 'circuit__name', 'circuit_name', 'created_by__username')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('created_by',)
    inlines = [RaidSignupInline, GMOverrideLogInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'targets', 'date', 'start_time', 'circuit', 'circuit_name', 'is_public', 'status', 'notes'),
        }),
        ('Audit', {
            'fields': ('created_by', 'posted_by_name', 'created_at'),
            'classes': ('collapse',),
        }),
        ('GM Override', {
            'fields': ('gm_override_reason',),
            'description': (
                'If you are scheduling this event past a hard conflict, '
                'provide a reason here. This is logged for the audit trail.'
            ),
        }),
    )

    def circuit_display(self, obj):
        return obj.circuit_display
    circuit_display.short_description = 'Circuit'

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

        reason = form.cleaned_data.get('gm_override_reason', '').strip()
        if reason:
            GMOverrideLog.objects.create(
                event=obj,
                overridden_by=request.user,
                reason=reason,
            )


@admin.register(RaidTarget)
class RaidTargetAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'description')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(GMOverrideLog)
class GMOverrideLogAdmin(admin.ModelAdmin):
    list_display = ('event', 'overridden_by', 'created_at', 'reason_short')
    readonly_fields = ('event', 'overridden_by', 'reason', 'created_at')
    list_filter = ('created_at',)

    def reason_short(self, obj):
        return obj.reason[:80] + ('…' if len(obj.reason) > 80 else '')
    reason_short.short_description = 'Reason'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
