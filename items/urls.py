from django.urls import path

from . import views

app_name = "items"
urlpatterns = [
    path("search", views.search, name="search"),
    path("discovered", views.discovered_items, name="discovered"),
    path("view/<int:item_id>", views.view_item, name="view"),
    path("bis", views.best_in_slot, name="bis"),
    path("bis/<int:class_id>", views.best_in_slot, name="bis_class"),
    path("bis/history/", views.bis_history, name="bis_history"),
    path("bis/<int:class_id>/history/", views.bis_history, name="bis_class_history"),
    path("bis/<int:class_id>/slot/<str:expansion>/<str:slot>/", views.bis_slot_entries, name="bis_slot_entries"),
    path("bis/<int:class_id>/edit/<str:expansion>/<str:slot>/", views.bis_edit_slot, name="bis_edit_slot"),
    path('api/<int:item_id>/', views.item_detail_api, name='item_detail_api'),
    path('api/item-search/', views.item_name_search, name='item_name_search'),
]
