from datetime import datetime, timedelta


from django.shortcuts import render
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view


from conference.serializers import AuthorsSerializer
from conference.serializers import ArticlesSerializer


from conference.models import Authors
from conference.models import Articles
from account.models import CustomUser


mockUserID = 2 # Временные данные пользователя
mockModeratorID = 4 # Временные данные модератора

#-----------------------------<AUTHORS>------------------------------

# @api_view(['GET'])
# def getAuthors(request, format=None):
#     """
#     Возвращает список авторов
#     """
#     authors = Authors.objects.all()
#     serializer = AuthorsSerializer(authors, many=True)
#     return Response(serializer.data, status=200)


@api_view(['GET'])
def getAuthors(request, format=None):
    """
    Поиск и фильтрация авторов
    """

    query = request.GET.get('query')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    filteredAuthors = Authors.objects.all().filter(status='Enabled')
    
    # Применяем параметр поиска по middle_name
    if query:
        if not filteredAuthors.filter(middle_name=query).filter(status='Enabled').exists():
            return Response([])
        else:
            filteredAuthors = filteredAuthors.filter(middle_name__icontains=query)

    # Применяем параметры фильтрации по дате рождения
    if start_date and end_date:
        filteredAuthors = filteredAuthors.filter(date_of_birth__range=[start_date, end_date])
    elif start_date:
        filteredAuthors = filteredAuthors.filter(date_of_birth__gte=start_date)
    elif end_date:
        filteredAuthors = filteredAuthors.filter(date_of_birth__lte=end_date)

    # Если ни один параметр не указан, возвращаем весь список авторов
    if not (query or start_date or end_date):
        filteredAuthors = Authors.objects.all().filter(status='Enabled')

    # Если авторы не найдены
    if not filteredAuthors.exists():
        return Response([])

    # Используем сериализатор для преобразования queryset в JSON
    serializer = AuthorsSerializer(filteredAuthors, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def getAuthor(request, pk, format=None):
    if not Authors.objects.filter(pk=pk).exists():
        return Response({"message": "Автора с таким ID не существует!"}, status=404)
    
    author = Authors.objects.get(pk=pk)
    if request.method == 'GET':
        """
        Возвращает информацию об авторе по ID
        """
        serializer = AuthorsSerializer(author)
        return Response(serializer.data, status=200)


@api_view(['POST'])
def createAuthor(request, format=None):    
    """
    Добавляет нового автора
    """
    serializer = AuthorsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def updateAuthor(request, pk, format=None):
    """
    Обновляет информацию об авторе
    """
    if not Authors.objects.filter(pk=pk).exists():
        return Response({"message": "Автора с таким ID не существует!"}, status=400)
        
    author = Authors.objects.get(pk=pk)
    serializer = AuthorsSerializer(author, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response({"message": "Автор успешно изменен"}, status=200)
    

@api_view(["DELETE"])
def deleteAuthor(request, pk):
    if not Authors.objects.filter(pk=pk).exists():
        return Response({"message": "Автора с таким ID не существует!"}, status=400)

    author = Authors.objects.get(pk=pk)
    author.status = 'Deleted'
    author.save()

    return Response({"message": "Автор успешно удален"}, status=200)


@api_view(["GET"])
def getAuthorImage(request, pk):
    if not Authors.objects.filter(pk=pk).exists():
        return Response({"message": "Автора с таким ID не существует!"}, status=400)

    author = Authors.objects.get(pk=pk)
    return HttpResponse(author.image, content_type="image/png")


#----------------------------<ARTICLES>------------------------------

@api_view(["GET"])
def getArticles(request):
    """
    Возвращает список статей
    """
    user = CustomUser.objects.get(pk=mockModeratorID)
    userID = user.id

    if user.is_moderator: # Проверяем, является ли пользователь модератором
        articles = Articles.objects.exclude(status__in='Deleted')  # Модератору доступны все статьи
    else:
        articles = Articles.objects.filter(user_id=userID).exclude(status__in='Deleted')
    
    serializer = ArticlesSerializer(articles, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def getArticle(request, pk):
    """
    Возвращает информацию о статье по ID
    """
    user = CustomUser.objects.get(pk=mockUserID)
    userID = user.id

    if not Articles.objects.filter(pk=pk).exists():
        return Response({"message": "Статьи с таким ID не существует!"}, status=400)

    if user.is_moderator: # Проверяем, является ли пользователь модератором
        article = Articles.objects.get(pk=pk)

    if user.is_moderator: # Проверяем, является ли пользователь модератором
        article = Articles.objects.get(pk=pk)
        serializer = ArticlesSerializer(article, many=False)
        return Response(serializer.data)

    if not Articles.objects.filter(pk=pk).filter(user_id=userID).exists():
        return Response({"message": "У вас нет доступа к статье"}, status=404)

    article = Articles.objects.get(pk=pk, user_id=userID)
    serializer = ArticlesSerializer(article, many=False)

    return Response(serializer.data)

@api_view(['PUT'])
def updateArticle(request, pk):
    """
    Обновляет информацию о статье
    """
    user = CustomUser.objects.get(pk=mockUserID)
    userID = user.id

    try:
        article = Articles.objects.get(id=pk, user_id=userID)
    except Articles.DoesNotExist:
        return Response({"message": "Статьи с таким ID не существует!"}, status=400)

    serializer = ArticlesSerializer(article, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response({"message": "Данные не верны!"}, status=400)

    return Response({"message": "Статья успешно изменена"}, status=200)


@api_view(["DELETE"])
def deleteArticle(request, pk):
    """
    Удаляет информацию о статье
    """
    user = CustomUser.objects.get(pk=mockUserID)
    userID = user.id

    if not Articles.objects.filter(pk=pk).filter(user_id=userID).exists():
        return Response({"message": "Статьи с таким ID не существует!"}, status=400)

    article = Articles.objects.get(pk=pk, user_id=userID)
    article.status = "Deleted"
    article.save()

    return Response({"message": "Статья успешно удалена"}, status=200)


#---------------------<UPDATE Articles status>-----------------------

@api_view(["PUT"])
def acceptArticle(request, pk):
    """
    Обновляет статьи автором
    """
    user = CustomUser.objects.get(pk=mockUserID)
    userID = user.id

    try:
        article = Articles.objects.get(pk=pk)
    except Articles.DoesNotExist:
        return Response({"message": "Статья не найдена"}, status=404)
    
    if article.status != 'Registered':
        return Response({"message": "Статус статьи не может быть изменен"}, status=400)
    
    requestStatus = request.data.get('status')
    if requestStatus not in ['Moderating', 'Deleted']:
        return Response({"message": "Недопустимый статус статьи"}, status=400)
    
    article.status = requestStatus
    article.user = CustomUser.objects.get(pk=mockUserID)
    article.approving_date=datetime.now()
    article.save()

    return Response({"message": "Статус статьи успешно изменен"}, status=200)


@api_view(["PUT"])
def confirmArticle(request, pk):
    """
    Обновляет статьи модератором
    """
    user = CustomUser.objects.get(pk=mockUserID)
    userID = user.id

    try:
        article = Articles.objects.get(pk=pk)
    except Articles.DoesNotExist:
        return Response({"message": "Статья не найдена"}, status=404)
    
    if article.status != 'Moderating':
        return Response({"message": "Статус статьи не может быть изменен"}, status=400)
    
    requestStatus = request.data.get('status')
    if requestStatus not in ['Approved', 'Denied']:
        return Response({"message": "Недопустимый статус статьи"}, status=400)
    
    article.status = requestStatus
    article.moderator = CustomUser.objects.get(pk=mockUserID)
    article.publication_date=datetime.now()
    article.save()

    return Response({"message": "Статус статьи успешно изменен"}, status=200)


#-----------------------<Authors - Articles>-------------------------

@api_view(["POST"])
def addAuthorToArticle(request, pk):
    """
    Добавляет автора в заявку[статью]
    """
    user = CustomUser.objects.get(pk=mockUserID)
    userID = user.id

    if not Authors.objects.filter(pk=pk).exists():
        return Response({"message": "Автора с таким ID не существует!"}, status=400)
    
    author = Authors.objects.get(pk=pk)
    article = Articles.objects.filter(status='Registered').filter(user_id=userID).last()

    if article is None:
        article = Articles.objects.create()

    article.authors.add(author)
    article.user = CustomUser.objects.get(pk=mockUserID)
    article.save()

    return Response({"message": "Автор успешно добавлен в заявку"}, status=200)


@api_view(["DELETE"])
def deleteAuthorFromArticle(request, article_id, author_id):
    """
    Удаляет автора из заявки[статьи]
    """
    user = CustomUser.objects.get(pk=mockUserID)
    userID = user.id
    
    if not Articles.objects.filter(pk=article_id, user_id=userID, authors__id=author_id).exists():
        return Response({"message": "Статьи с таким ID или автора с таким ID не существует!"}, status=400)

    article = Articles.objects.get(pk=article_id, user_id=userID, authors__id=author_id)
    article.authors.remove(Authors.objects.get(pk=author_id))
    article.save

    return Response({"message": "Автор успешно удален из заявки"}, status=200)
