from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static

from conference.models import *

# Create your views here.

menu = [
    {'title': "Главная", 'url_name': 'authors'},
    {'title': "Добавить статью", 'url_name': 'add_page'},
    {'title': "Обратная связь", 'url_name': 'contact'},
    {'title': "Войти", 'url_name': 'login'}
]

#<!---------------------------------------------------------------------------------------------------------!>

def index(request):

    query = request.GET.get('search')
    AuthorsData = Authors.objects.filter(middle_name=query).filter(status='Enabled') if query else Authors.objects.filter(status='Enabled')

    print(AuthorsData)

    context = {
        'menu': menu, 
        'authors': AuthorsData, 
        'title': 'Главная страница',
        "search_query": query if query else ""

    }
    
    return render(request, 'conference/index.html', context)



#getAuthor() - это представление, которое получает запись автора по ID используя функцию FindAuthorByID() и передает его в шаблон author.html.
def getAuthor(request, id):

    author = Authors.objects.get(pk=id)

    context = {
        'author': author,
        'menu': menu, 
        'title': 'Информация об авторе', 
    }  

    return render(request, 'conference/author.html', context)


def authorDelete(request, author_id):

    author = Author.objects.get(id=author_id)
    author.status = 'Deleted'
    author.save()

    return redirect("/")


#<!---------------------------------------------------------------------------------------------------------!>

def about(request):
    return render(request, 'conference/about.html', {'menu': menu, 'title': 'О сайте'})


#<!---------------------------------------------------------------------------------------------------------!>

def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


#<!---------------------------------------------------------------------------------------------------------!>

def addpage(request):
    return HttpResponse("Добавление статьи")


#<!---------------------------------------------------------------------------------------------------------!>

def contact(request):
    return HttpResponse("Обратная связь")


#<!---------------------------------------------------------------------------------------------------------!>

def login(request):
    return HttpResponse("Авторизация")
