from django.urls import path, re_path
 
from .views import *
 
urlpatterns = [
    # path('', index),

    path('authors/', index, name='authors'),
    path('authors/<int:id>/', author, name='author'), 
    path('filter/', filter, name='filter'),

    path('addpage/', addpage, name='add_page'),
    path('contact/', contact, name='contact'),
    path('login/', login, name='login'),
]