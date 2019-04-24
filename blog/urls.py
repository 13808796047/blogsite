from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.index, name='index'),
    path('post/<int:pk>', views.detail, name='detail'),
    path('archives/<str:year>/<str:month>', views.archives, name='archives'),
    path('category/<int:pk>', views.category, name='category'),
]
