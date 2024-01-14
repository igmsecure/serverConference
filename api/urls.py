from django.urls import path, include, re_path
from rest_framework import permissions


from conference.urls import urlpatterns as conference_urls
from account.urls import urlpatterns as account_urls


app_name = 'api'

urlpatterns = [
   
]

urlpatterns += conference_urls
urlpatterns += account_urls
