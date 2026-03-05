from django.contrib import admin

from dkp.models import (
    Auction,
    Bid,
    DKPTransaction,
    RaidAttendance,
    RaidCircuit,
    CircuitConfig,
    CircuitMembership,
    Mob,
    Raid
)


# Register your models here.
class RaidCircuitAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    list_filter = ['name',]
    search_fields = ['name', ]


class CircuitConfigAdmin(admin.ModelAdmin):
    pass


class CircuitMembershipAdmin(admin.ModelAdmin):
    list_display = ['member', 'circuit', 'role', 'status', 'current_dkp']
    list_filter = ['member']


class MobAdmin(admin.ModelAdmin):
    list_display = ['name', 'circuit', 'dkp', 'is_active']


class RaidAdmin(admin.ModelAdmin):
    list_display = ['date', 'circuit', 'labels']


class RaidAttendanceAdmin(admin.ModelAdmin):
    pass


class DKPTransactionAdmin(admin.ModelAdmin):
    pass


class AuctionAdmin(admin.ModelAdmin):
    pass


class BidAdmin(admin.ModelAdmin):
    pass


admin.site.register(RaidCircuit, RaidCircuitAdmin)
admin.site.register(CircuitConfig, CircuitConfigAdmin)
admin.site.register(CircuitMembership, CircuitMembershipAdmin)
admin.site.register(Mob, MobAdmin)
admin.site.register(Raid, RaidAdmin)
admin.site.register(RaidAttendance, RaidAttendanceAdmin)
admin.site.register(DKPTransaction, DKPTransactionAdmin)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid, BidAdmin)
