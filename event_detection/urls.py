from django.urls import path
from . import views

urlpatterns = [
    path('', views.search, name='search'),
    path('update_search_result', views.update_search_result, name='update_search_result'),
    path('system_management', views.system_management, name='system_management'),
    path('about', views.about, name='about'),
]