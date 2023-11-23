from django.urls import path
from conference.views import *

urlpatterns = [

    #-------------------------<AUTHORS>---------------------------

    # Набор методов для услуг (Автор)
    path('authors/', getAuthors),  # GET
    path('authors/<int:pk>/', getAuthor),  # GET
    path('authors/create/', createAuthor),  # POST
    path('authors/<int:pk>/update/', updateAuthor),  # PUT
    path('authors/<int:pk>/delete/', deleteAuthor),  # DELETE    
    path('authors/<int:pk>/image/', getAuthorImage),  # GET

    #-------------------------<ARTILES>---------------------------
    
    # Набор методов для заявок (Публикация статьи)
    path('articles/', getArticles),  # GET
    path('articles/<int:pk>/', getArticle),  # GET
    path('articles/<int:pk>/update/', updateArticle),  # PUT
    path('articles/<int:pk>/delete/', deleteArticle),  # DELETE 

    path('articles/<int:pk>/accept/', acceptArticle),  # PUT
    path('articles/<int:pk>/confirm/', confirmArticle),  # PUT

    #-------------------<Authors - Articles>---------------------
    path('authors/<int:pk>/add/', addAuthorToArticle),  # POST
    path('articles/<int:article_id>/delete_author/<int:author_id>/', deleteAuthorFromArticle),  # DELETE

]