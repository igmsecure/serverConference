from django.urls import path, re_path
 
from .views import *
 
urlpatterns = [
    # path('', index),
    path('authors/', index, name='authors'),
    path('authors/<int:id>/', author, name='author'), 
]
