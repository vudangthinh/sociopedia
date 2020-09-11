from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup, name='signup'),

    path('search', views.search, name='search'),
    path('update_search_result', views.update_search_result, name='update_search_result'),
    path('system_management', views.system_management, name='system_management'),
    path('data_analysis', views.data_analysis, name='data_analysis'),
    path('word_cloud', views.word_cloud, name='word_cloud'),
    path('knowledge_graph', views.knowledge_graph, name='knowledge_graph'),
    path('view_tweets/<int:pk>/', views.view_tweets, name='view_tweets'),

    path('ajax/keyword', views.delete_keyword, name='delete_keyword'),
    path('ajax/filter_tweets_intime', views.filter_tweets_intime, name='filter_tweets_intime'),

    path('', views.home, name='home'),
    # path('home', views.home, name='home'),
    path('about', views.about, name='about'),
]