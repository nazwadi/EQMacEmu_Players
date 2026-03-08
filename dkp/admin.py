from django.contrib import admin
from dkp.models import (
    Auction, Bid, DKPTransaction, RaidAttendance,
    RaidCircuit, CircuitConfig, CircuitMembership, Mob, Raid
)


class CircuitConfigInline(admin.StackedInline):
    model = CircuitConfig
    extra = 0
    can_delete = False


class RaidAttendanceInline(admin.TabularInline):
    model = RaidAttendance
    extra = 0
    fields = ['member', 'attendance_status', 'attendance_notes']
    autocomplete_fields = ['member']


class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    fields = ['member', 'bid_amount', 'status']
    readonly_fields = ['submitted_at']


@admin.register(RaidCircuit)
class RaidCircuitAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'is_public', 'created_at']
    list_filter = ['is_active', 'is_public']
    search_fields = ['name']
    inlines = [CircuitConfigInline]


@admin.register(CircuitConfig)
class CircuitConfigAdmin(admin.ModelAdmin):
    list_display = ['circuit', 'dkp_cap', 'dkp_overcap', 'minimum_bid', 'public_bids']
    list_filter = ['public_bids']


@admin.register(CircuitMembership)
class CircuitMembershipAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'member', 'circuit', 'role', 'status', 'current_dkp', 'lifetime_earned_dkp', 'lifetime_spent_dkp']
    list_filter = ['circuit', 'role', 'status']
    search_fields = ['display_name', 'member__username']
    readonly_fields = ['joined_at']


@admin.register(Mob)
class MobAdmin(admin.ModelAdmin):
    list_display = ['name', 'circuit', 'dkp', 'is_active']
    list_filter = ['circuit', 'is_active']
    search_fields = ['name']


@admin.register(Raid)
class RaidAdmin(admin.ModelAdmin):
    list_display = ['date', 'circuit', 'labels', 'is_private', 'created_by']
    list_filter = ['circuit', 'is_private']
    search_fields = ['labels', 'notes']
    date_hierarchy = 'date'
    inlines = [RaidAttendanceInline]


@admin.register(RaidAttendance)
class RaidAttendanceAdmin(admin.ModelAdmin):
    list_display = ['raid', 'member', 'attendance_status']
    list_filter = ['attendance_status']
    search_fields = ['member__display_name']


@admin.register(DKPTransaction)
class DKPTransactionAdmin(admin.ModelAdmin):
    list_display = ['member', 'circuit_name', 'transaction_type', 'amount', 'item_name', 'transaction_date', 'created_by']
    list_filter = ['transaction_type', 'member__circuit']
    search_fields = ['member__display_name', 'item_name']
    readonly_fields = ['transaction_date']
    date_hierarchy = 'transaction_date'

    def circuit_name(self, obj):
        return obj.member.circuit.name
    circuit_name.short_description = 'Circuit'


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'circuit', 'status', 'opened_at', 'created_by']
    list_filter = ['status', 'circuit']
    search_fields = ['item_name']
    readonly_fields = ['opened_at', 'closed_at']
    inlines = [BidInline]


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['member', 'auction', 'bid_amount', 'status', 'submitted_at']
    list_filter = ['status']
    search_fields = ['member__display_name', 'auction__item_name']
    readonly_fields = ['submitted_at', 'modified_at']