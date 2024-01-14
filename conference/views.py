from datetime import datetime, timedelta


from django.shortcuts import render
from rest_framework.response import Response
from django.http import HttpResponse
import requests 
import json

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.text import slugify


from conference.serializers import AuthorsSerializer
from conference.serializers import ArticlesSerializer


from conference.models import Authors
from conference.models import Articles
from account.models import CustomUser


from rest_framework.decorators import permission_classes
from account.permissions import *
from account.JWTConfig import createAccessToken, createRefreshToken, getJwtPayload, getAccessToken, getRefreshToken




from django.core.files.base import ContentFile
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import default_storage
from django.http import HttpResponse

from io import BytesIO
from base64 import b64encode, b64decode

def upload_image_to_s3(image_data, object_name, content_type):
    storage = S3Boto3Storage()
    image_data = b64decode(image_data)
    image_file = ContentFile(image_data)
    image_file.name = object_name
    storage.save(object_name, image_file)



def uploadAuthorImage(request, serializedata):
    middle_name = serializedata.get('middle_name')
    image_data = serializedata.get('image')
    print(image_data)
    # middle_name_for_path = slugify(middle_name.split(' ', 1)[1])
    image_path = middle_name + '.png'
    upload_image_to_s3(image_data, image_path, 'image/png')


secretKey = "WTXKmg65e0zYNzFEaZ"

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

    # token = getAccessToken(request)
    # payload = getJwtPayload(token)
    # user_id = payload['user_id']

    if 'Authorization' in request.headers:
        authHeader = request.headers.get('Authorization')
        token = authHeader.split(' ')[1] if authHeader else None
        payload = getJwtPayload(token)
        user_id = payload["user_id"]

    
    try: 
        article = Articles.objects.filter(user_id=user_id).filter(status='Registered')
        article_serializer = ArticlesSerializer(article, many=True)
    except:
        article_serializer = []

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

    return Response({
        'article': article_serializer.data if article_serializer else None,
        'authors': serializer.data 
    }, status=status.HTTP_200_OK)

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


@swagger_auto_schema(method='POST', request_body=AuthorsSerializer)
@api_view(['POST'])
@permission_classes([IsModerator])
def createAuthor(request, format=None):    
    """
    Добавляет нового автора
    """
    serializer = AuthorsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        uploadAuthorImage(request, serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsModerator])
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
@permission_classes([IsModerator])
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

# @swagger_auto_schema(method='GET')
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def getArticles(request):
#     """
#     Возвращает список статей
#     """
#     # Исходный блок кода
#     # token = getAccessToken(request)
#     # payload = getJwtPayload(token)
#     # user_id = payload["user_id"]

#     # Блок кода для работы с 6-й ЛР
#     authHeader = request.headers.get('Authorization')
#     token = authHeader.split(' ')[1] if authHeader else None
#     payload = getJwtPayload(token)
#     user_id = payload["user_id"]
#     print(token)

#     user = CustomUser.objects.get(pk=payload["user_id"])
#     if user.is_moderator: # Проверяем, является ли пользователь модератором
#         articles = Articles.objects.exclude(status__in='Deleted')  # Модератору доступны все статьи
#     else:
#         articles = Articles.objects.filter(user_id=user_id).exclude(status='Deleted')
    
#     serializer = ArticlesSerializer(articles, many=True)
#     return Response(serializer.data)




@swagger_auto_schema(method='GET')
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getArticles(request):
    """
    Возвращает список статей
    """
    # Исходный блок кода
    # token = getAccessToken(request)
    # payload = getJwtPayload(token)
    # user_id = payload["user_id"]


    status = request.GET.get('status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Блок кода для работы с 6-й ЛР
    authHeader = request.headers.get('Authorization')
    token = authHeader.split(' ')[1] if authHeader else None
    payload = getJwtPayload(token)
    user_id = payload["user_id"]
    print(token)

    user = CustomUser.objects.get(pk=payload["user_id"])

    filteredArticles = Articles.objects.exclude(status='Deleted')

    if user.is_moderator: # Проверяем, является ли пользователь модератором
        if status:
            filteredArticles = filteredArticles.filter(status=status).exclude(status='Registered')
        # Применяем параметры фильтрации по дате формирования
        if start_date and end_date:
            filteredArticles = filteredArticles.filter(approving_date__range=[start_date, end_date]).exclude(status='Registered')
        elif start_date:
            filteredArticles = filteredArticles.filter(approving_date__gte=start_date).exclude(status='Registered')
        elif end_date:
            filteredArticles = filteredArticles.filter(approving_date__lte=end_date).exclude(status='Registered')
        # Если ни один параметр не указан, возвращаем весь список авторов
        if not (status or start_date or end_date):
            filteredArticles = Articles.objects.exclude(status='Deleted').exclude(status='Registered')
    else:
        filteredArticles = Articles.objects.filter(user_id=user_id).exclude(status='Deleted')

    # Если авторы не найдены
    if not filteredArticles.exists():
        return Response([])

    serializer = ArticlesSerializer(filteredArticles, many=True)
    return Response(serializer.data)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getArticle(request, pk):
    """
    Возвращает информацию о статье по ID
    """
    # Исходный блок кода
    # token = getAccessToken(request)
    # payload = getJwtPayload(token)
    # user_id = payload["user_id"]

    # Блок кода для работы с 6-й ЛР
    authHeader = request.headers.get('Authorization')
    token = authHeader.split(' ')[1] if authHeader else None
    payload = getJwtPayload(token)
    user_id = payload["user_id"]
    print(token)

    user = CustomUser.objects.get(pk=payload["user_id"])

    if user.is_moderator: # Проверяем, является ли пользователь модератором
        article = Articles.objects.get(pk=pk)
        serializer = ArticlesSerializer(article, many=False)
        return Response(serializer.data)

    
    if not Articles.objects.filter(pk=pk).exists():
        return Response({"message": "Статьи с таким ID не существует!"}, status=400)

    if not Articles.objects.filter(pk=pk).filter(user_id=user_id).exists():
        return Response({"message": "У вас нет доступа к статье"}, status=404)

    article = Articles.objects.get(pk=pk, user_id=user_id)
    serializer = ArticlesSerializer(article, many=False)

    return Response(serializer.data, status=200)

@swagger_auto_schema(method='PUT', request_body=ArticlesSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateArticle(request, pk):
    """
    Обновляет информацию о статье
    """

    # Исходный блок кода
    # token = getAccessToken(request)
    # payload = getJwtPayload(token)
    # user_id = payload["user_id"]


    # Блок кода для работы с 6-й ЛР
    authHeader = request.headers.get('Authorization')
    token = authHeader.split(' ')[1] if authHeader else None
    payload = getJwtPayload(token)
    user_id = payload["user_id"]
    print(token)

    try:
        article = Articles.objects.get(id=pk, user_id=user_id)
    except Articles.DoesNotExist:
        return Response({"message": "Статьи с таким ID не существует!"}, status=400)

    serializer = ArticlesSerializer(article, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response({"message": "Данные не верны!"}, status=400)

    return Response({"message": "Статья успешно изменена"}, status=200)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteArticle(request, pk):
    """
    Удаляет информацию о статье
    """

    # Исходный блок кода
    # token = getAccessToken(request)
    # payload = getJwtPayload(token)
    # user_id = payload["user_id"]

    # Блок кода для работы с 6-й ЛР
    authHeader = request.headers.get('Authorization')
    token = authHeader.split(' ')[1] if authHeader else None
    payload = getJwtPayload(token)
    user_id = payload["user_id"]
    print(token)

    if not Articles.objects.filter(pk=pk).filter(user_id=user_id).exists():
        return Response({"message": "Статьи с таким ID не существует!"}, status=400)

    article = Articles.objects.get(pk=pk, user_id=user_id)
    article.status = "Deleted"
    article.save()

    return Response({"message": "Статья успешно удалена"}, status=200)


#---------------------<UPDATE Articles status>-----------------------

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def acceptArticle(request, pk):
    """
    Обновляет статьи автором
    """

    # Исходный блок кода
    # token = getAccessToken(request)
    # payload = getJwtPayload(token)
    # userID = payload["user_id"]

    # Блок кода для работы с 6-й ЛР
    authHeader = request.headers.get('Authorization')
    token = authHeader.split(' ')[1] if authHeader else None
    payload = getJwtPayload(token)
    userID = payload["user_id"]
    print(token)

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
    article.user = CustomUser.objects.get(pk=userID)
    article.approving_date=datetime.now()
    article.save()
    AsyncReviewing(request, pk, userID)

    return Response({"message": "Статус статьи успешно изменен"}, status=200)


@api_view(["PUT"])
@permission_classes([IsModerator])
def confirmArticle(request, pk):
    """
    Обновляет статьи модератором
    """

    # Исходный блок кода
    # token = getAccessToken(request)
    # payload = getJwtPayload(token)
    # user_id = payload["user_id"]

    # Блок кода для работы с 6-й ЛР
    authHeader = request.headers.get('Authorization')
    token = authHeader.split(' ')[1] if authHeader else None
    payload = getJwtPayload(token)
    user_id = payload["user_id"]
    print(token)


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
    article.moderator = CustomUser.objects.get(pk=payload["user_id"])
    article.publication_date=datetime.now()
    article.save()

    return Response({"message": "Статус статьи успешно изменен"}, status=200)


#-----------------------<Authors - Articles>-------------------------

@swagger_auto_schema(method='POST')
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def addAuthorToArticle(request, pk):
    """
    Добавляет автора в заявку[статью]
    """

    # Исходный блок кода
    # token = getAccessToken(request)
    # payload = getJwtPayload(token)
    # user_id = payload["user_id"]


    # Блок кода для работы с 6-й ЛР
    authHeader = request.headers.get('Authorization')
    token = authHeader.split(' ')[1] if authHeader else None
    payload = getJwtPayload(token)
    user_id = payload["user_id"]
    print(token)
    
    if not Authors.objects.filter(pk=pk).exists():
        return Response({"message": "Автора с таким ID не существует!"}, status=400)
    
    author = Authors.objects.get(pk=pk)
    article = Articles.objects.filter(status='Registered').filter(user_id=user_id).last()

    if article is None:
        article = Articles.objects.create()

    article.authors.add(author)
    article.user = CustomUser.objects.get(pk=payload["user_id"])
    article.save()

    return Response({"message": "Автор успешно добавлен в заявку"}, status=200)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteAuthorFromArticle(request, article_id, author_id):
    """
    Удаляет автора из заявки[статьи]
    """

    # Исходный блок кода
    # token = getAccessToken(request)
    # payload = getJwtPayload(token)
    # user_id = payload["user_id"]

    # Блок кода для работы с 6-й ЛР
    authHeader = request.headers.get('Authorization')
    token = authHeader.split(' ')[1] if authHeader else None
    payload = getJwtPayload(token)
    user_id = payload["user_id"]
    print(token)
    
    if not Articles.objects.filter(pk=article_id, user_id=user_id, authors__id=author_id).exists():
        return Response({"message": "Статьи с таким ID или автора с таким ID не существует!"}, status=400)

    article = Articles.objects.get(pk=article_id, user_id=user_id, authors__id=author_id)
    article.authors.remove(Authors.objects.get(pk=author_id))
    article.save

    return Response({"message": "Автор успешно удален из заявки"}, status=200)


#------------------------<Async Service>--------------------------

def AsyncReviewing(request, articleID, userID):
    """
    Возвращает список авторов
    """
    successMessage = "Review processing request sent successfully"
    errorMassage = "Failed to send review processing request"

    url = 'http://localhost:8080/asyncProcessReviewing'
    data = {
        "articleID": articleID,
        'userID': userID
    }
    headers = {'Content-type': 'application/json'}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        return Response({"message": successMessage}, status=status.HTTP_200_OK)
    else:
        return Response({"message": errorMassage}, status=status.HTTP_400_OK)



# async update method
@api_view(['PUT'])
def updateArticleReviewing(request, articleID):
    """
    Обновляет информацию о статье
    """

    requestSecretKey = request.data.get('secretKey')

    if secretKey != requestSecretKey:
        return Response({'message': 'Secret key does not match'}, status=400)

    try:
        article = Articles.objects.get(id=articleID, user_id=request.data.get('userID'))
    except Articles.DoesNotExist:
        return Response({"message": "Проверьте ваши данные"}, status=400)

    article.review = request.data.get('result')
    article.save()

    return Response({"message": "Статья успешно изменена [оценка рецензирования]"}, status=200)






