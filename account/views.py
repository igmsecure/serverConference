import ast
import time

from operator import itemgetter
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt import authentication


from .JWTConfig import createAccessToken, createRefreshToken, getJwtPayload, getAccessToken, getRefreshToken
from .permissions import *
from .serializers import *


access_token_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
refresh_token_lifetime = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()



@api_view(["POST"])
def loginView(request):
    # Ensure email and passwords are posted properly
    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    password = serializer.validated_data['password']


    # Check credentials
    user = authenticate(email=email, password=password)
    if user is None:
        message = {'message': 'Проверьте введенные данные'}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    # Create new access and refresh token
    access_token = createAccessToken(user.id)

    # Add access token to redis for validating by other services
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'is_moderator': user.is_moderator,
        'access_token': access_token
    }
    cache.set(access_token, user_data, access_token_lifetime)

    # Create response object
    response = Response(user_data, status=status.HTTP_201_CREATED)
    # Set access token in cookie
    response.set_cookie('access_token', access_token, httponly=False, expires=access_token_lifetime, samesite="Lax")

    return response


@api_view(["POST"])
def registerView(request):
    # Ensure username and passwords are posted is properly
    serializer = RegistrationSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Create user
    user = serializer.save()
    message = {
        'message': 'Пользователь успешно зарегистрирован',
        'user_id': user.id
    }

    return Response(message, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def checkView(request):
    access_token = getAccessToken(request)

    if access_token is None:
        message = {"message": "Token is not found"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    # Check is token in Redis
    if not cache.has_key(access_token):
        message = {"message": "Token is not valid"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    user_data = cache.get(access_token)

    return Response(user_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def logoutView(request):
    access_token = request.COOKIES.get('access_token')

    # Check access token is in cookie
    if access_token is None:
        message = {"message": "Token is not found in cookie"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    #  Check access token is in Redis
    if cache.has_key(access_token):
        # Delete access token from Redis
        cache.delete(access_token)

    # Create response object
    message = {"message": "Logged out successfully!"}
    response = Response(message, status=status.HTTP_200_OK)
    # Delete access token from cookie
    response.delete_cookie('access_token')

    return response