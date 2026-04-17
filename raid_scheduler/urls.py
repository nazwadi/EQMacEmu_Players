from django.urls import path

from . import views

app_name = 'raid_scheduler'

urlpatterns = [
    path('', views.board, name='board'),
    path('schedule/', views.schedule, name='schedule'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    path('event/<int:pk>/cancel/', views.cancel_event, name='cancel_event'),
    path('event/<int:pk>/delete/', views.delete_event, name='delete_event'),
    path('event/<int:pk>/edit/', views.edit_event, name='edit_event'),
    path('event/<int:pk>/ics/', views.event_ics, name='event_ics'),
    path('conflict-check/', views.conflict_check, name='conflict_check'),
    path('event/<int:pk>/rsvp/', views.rsvp_event, name='rsvp_event'),
    path('history/', views.history, name='history'),
    path('calendar.ics', views.calendar_feed, name='calendar_feed'),
]
