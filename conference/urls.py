from django.urls import path, re_path, include

from .views import *
 
urlpatterns = [
    # path('', index),

    path('authors/', index, name='authors'),
    path('authors/<int:id>/', getAuthor, name='author'), 
    path('delete-author/<int:author_id>', authorDelete, name="delete-author"),


    path('addpage/', addpage, name='add_page'),
    path('contact/', contact, name='contact'),
    path('login/', login, name='login'),
]
