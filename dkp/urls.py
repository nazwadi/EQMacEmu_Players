from django.urls import path

from . import views

app_name = "dkp"
urlpatterns = [
    path("", views.circuit_list, name="circuit_list"),
    path("standings/<int:circuit_id>/", views.standings, name="standings"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/<int:membership_id>/", views.dashboard, name="dashboard_member"),
    path("raids/<int:circuit_id>/", views.raid_list, name="raid_list"),
    path("raid/<int:raid_id>/", views.raid_detail, name="raid_detail"),
    path("manage/<int:circuit_id>/raids/", views.raid_manage_list, name="raid_manage_list"),
    path("manage/<int:circuit_id>/raids/create/", views.raid_create, name="raid_create"),
    path("manage/raid/<int:raid_id>/", views.raid_manage_detail, name="raid_manage_detail"),
    path("manage/raid/<int:raid_id>/delete/", views.raid_delete, name="raid_delete"),
    path("auctions/<int:circuit_id>/", views.auction_list, name="auction_list"),
    path("auction/<int:auction_id>/", views.auction_detail, name="auction_detail"),
    path("manage/auction/<int:auction_id>/", views.auction_manage, name="auction_manage"),
    path("auction/<int:auction_id>/state/", views.auction_state, name="auction_state"),
    path("auction/<int:auction_id>/bid/", views.bid_submit, name="bid_submit"),
    path("auction/<int:auction_id>/retract/", views.bid_retract, name="bid_retract"),
    path("transactions/<int:membership_id>/", views.transaction_history, name="transaction_history"),
    path("manage/<int:circuit_id>/members/", views.member_list, name="member_list"),
    path("circuit/<int:circuit_id>/join/", views.circuit_join, name="circuit_join"),
    path("manage/<int:circuit_id>/config/", views.circuit_config, name="circuit_config"),
    path('attendance/<int:membership_id>/', views.attendance_history, name='attendance_history'),
    path('manage/<int:circuit_id>/mobs/', views.mob_manage, name='mob_manage'),
    path('manage/<int:circuit_id>/npc-search/', views.npc_search, name='npc_search'),
    path('manage/<int:circuit_id>/mob/<int:mob_id>/loot/', views.mob_loot_items, name='mob_loot_items'),
    path('manage/raid/<int:raid_id>/direct-award/', views.direct_award_view, name='direct_award'),
    path('manage/<int:circuit_id>/adjustments/', views.circuit_adjustments, name='circuit_adjustments'),
]
