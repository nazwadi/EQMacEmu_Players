from django.urls import path

from . import views

app_name = "items"
urlpatterns = [
    path("search", views.search, name="search"),
    path("discovered", views.discovered_items, name="discovered"),
    path("view/<int:item_id>", views.view_item, name="view"),
    path("bis", views.best_in_slot, name="bis"),
    path("bis/<int:class_id>", views.best_in_slot, name="bis"),
    path('api/<int:item_id>/', views.item_detail_api, name='item_detail_api'),
]
