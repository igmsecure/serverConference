import ast
import time

from operator import itemgetter
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.core.cache import cache


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.text import slugify


from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt import authentication


from .JWTConfig import createAccessToken, createRefreshToken, getJwtPayload, getAccessToken, getRefreshToken
from .permissions import *
from .authSerializers import *


access_token_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
refresh_token_lifetime = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()


class RegisterView(APIView):
    @swagger_auto_schema(request_body=UserRegisterSerializer)
    def post(self, request):  
        # Ensure username and passwords are posted is properly
        serializer = UserRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create user
        user = serializer.save()
        message = {
            'message': 'User registered successfully', 
            'user_id': user.id
        }
        return Response(message, status=status.HTTP_201_CREATED)

    
class LoginView(APIView):
    @swagger_auto_schema(request_body=UserLoginSerializer)
    def post(self, request):
        # Ensure email and passwords are posted properly
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Check credentials
        user = authenticate(email=email, password=password)
        if user is None:
            message = {"message": "Проверьте введенные данные"}
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)
        
        # Create new access and refresh token
        access_token = createAccessToken(user.id)
        refresh_token = createRefreshToken(user.id)

        # Add access token to redis for validating by other services
        user_data = {
            "user_id": user.id,
            "email" : user.email,
            'username': user.username,
            'is_moderator': user.is_moderator,
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        cache.set(access_token, user_data, access_token_lifetime)

        # Create response object
        response = Response(user_data, status=status.HTTP_201_CREATED)
        # Set access token in cookie
        response.set_cookie('access_token', access_token, httponly=True, expires=access_token_lifetime,  samesite="Lax")
        # Set refresh token in cookie
        response.set_cookie('refresh_token', refresh_token, httponly=True, expires=refresh_token_lifetime,  samesite="Lax")

        return response
    
class RefresfTokenView(APIView):
    def get(self, request):
        # token = request.COOKIES.get('refresh_token')

        authHeader = request.headers.get('Authorization')
        token = authHeader.split(' ')[1] if authHeader else None



        # Ensure token is in
        if token is None:
            message = {"message": "Token is not found in cookie"}
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)
        
        # Ensure token is valid
        try:
            payload = getJwtPayload(token)
        except Exception as e:
            message = {"message": "Invalid Token, " + str(e)}
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)
        
        # Ensure user still exists
        try:
            user = CustomUser.objects.get(pk=payload["user_id"])
        except Exception as e:
            message = {"message": "User not found"+str(e)}
            return Response(message, status=status.HTTP_404_NOT_FOUND)
        
        # Ensure token is refresh token
        if payload["token_type"] != "refresh":
            message = {"message": "Token type is not refresh"}
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)

        # Check is token in Redis blacklist
        if cache.has_key(token):
            message = {"message": "Token is in Blacklist"}
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)

        # Create new access and refresh token
        access_token = createAccessToken(payload["user_id"])
        refresh_token = createRefreshToken(payload["user_id"])

        # Add old refresh token to redis for blacklist check
        refresh_token_lifetime = payload["exp"] - time.time()
        cache.set(token, payload["user_id"], refresh_token_lifetime)

        # Add access token to redis for validating by other services
        user_data = {
            "user_id": user.id,
            "email" : user.email,
            'username': user.username,
            'is_moderator': user.is_moderator,
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        cache.set(access_token, user_data, access_token_lifetime)

        # Create response object
        response = Response(user_data, status=status.HTTP_201_CREATED)
        # Set access token in cookie
        response.set_cookie('access_token', access_token, httponly=True, expires=access_token_lifetime)
        # Set refresh token in cookie
        response.set_cookie('refresh_token', refresh_token, httponly=True, expires=refresh_token_lifetime)
        return response

class CheckLoginStatus(APIView):
    def get(self, request):
        # access_token = request.COOKIES.get('access_token')

        authHeader = request.headers.get('Authorization')
        access_token = authHeader.split(' ')[1] if authHeader else None
    
        if access_token is None:
            message = {"message": "Token is not found in cookie"}
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check is token in Redis 
        if not cache.has_key(access_token):
            message = {"message": "Token is not valid"}
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)

        user_data = cache.get(access_token)

        return Response(user_data, status=status.HTTP_200_OK)


class Logout(APIView):
    @swagger_auto_schema(method='GET')
    def get(self, request):
        # access_token = request.COOKIES.get('access_token')

        authHeader = request.headers.get('Authorization')
        access_token = authHeader.split(' ')[1] if authHeader else None



        refresh_token = request.COOKIES.get('refresh_token')



        # Check access token is in cookie
        if access_token is None: 
            message = {"message": "Token is not found in cookie"}
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)
        
        #  Check access token is in Redis
        if cache.has_key(access_token):
            # Delete access token from Redis
            cache.delete(access_token)
        
        # Check refresh token is in cookie
        if refresh_token is not None:
            # Ensure refresh token is valid
            try:
                payload = getJwtPayload(refresh_token)
                # Check refresh token is not in Redis(not blacklisted)
                if not cache.has_key(refresh_token):
                    # Add refresh token to Redis blacklist
                    refresh_token_lifetime = payload["exp"] - time.time()
                    cache.set(refresh_token, payload["user_id"], refresh_token_lifetime)
            except Exception as e:
                # Create response object
                message = {"message": "Invalid Refresh Token, " + str(e)}
                response = Response(message, status=status.HTTP_401_UNAUTHORIZED)
                # Delete access token from cookie
                response.delete_cookie('access_token')
                # Delete refresh token from cookie
                response.delete_cookie('refresh_token')
                return response

        # Create response object
        message = {"message": "Logged out successfully!"}
        response = Response(message, status=status.HTTP_200_OK)
        # Delete access token from cookie
        response.delete_cookie('access_token')
        # Delete refresh token from cookie
        response.delete_cookie('refresh_token')
        return response