from django.urls import path
from . import views

urlpatterns = [
    path('', views.search, name='search'),
    path('update_search_result', views.update_search_result, name='update_search_result')
]