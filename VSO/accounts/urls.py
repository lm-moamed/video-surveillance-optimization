from django.urls import path
from . import views
from django.conf import settings

from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),

    path('profile/', views.user_profile, name='user_profile'),


    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    # path('dashboard/', views.home, name='dashboard'),
    path('dates/', views.date_list, name='dates'),
    path('streams/', views.stream_list, name='stream_list'),
    path('streams/<int:stream_id>/', views.stream_details, name='stream_details'),
    path('add_stream/', views.add_stream, name='add_stream'),
    path('edit_stream/<int:stream_id>/', views.edit_stream, name='edit_stream'),
    path('stream/<str:chosen_date>/', views.streams_list, name='streams_list'),
    path('records/<str:chosen_date>/<int:stream_id>/', views.record_list, name='records'),

    path('records/<str:path>/<str:video_filename>/', views.serve_video, name='serve_video'),

]
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
