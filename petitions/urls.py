from django.urls import path
from . import views

app_name = 'petitions'

urlpatterns = [
    # Player
    path('', views.petition_list, name='list'),
    path('new/', views.petition_create, name='create'),
    path('<int:pk>/', views.petition_detail, name='detail'),
    path('email-prefs/', views.player_email_preference, name='player_email_prefs'),

    # Staff queue & tools
    path('staff/', views.staff_petition_list, name='staff_list'),
    path('staff/tags/', views.staff_tag_list, name='staff_tags'),
    path('staff/canned-responses/', views.staff_canned_responses, name='staff_canned_responses'),
    path('staff/email-prefs/', views.staff_email_preference, name='staff_email_prefs'),

    # Per-petition actions
    path('<int:pk>/claim/', views.petition_claim, name='claim'),
    path('<int:pk>/status/', views.petition_status_update, name='status_update'),
    path('<int:pk>/priority/', views.petition_priority_update, name='priority_update'),
    path('<int:pk>/tags/', views.petition_update_tags, name='update_tags'),
    path('<int:pk>/lock/', views.petition_lock_toggle, name='lock_toggle'),
    path('attachment/<int:reply_pk>/', views.petition_attachment, name='attachment'),
]
