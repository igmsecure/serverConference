from rest_framework import serializers

from .models import *
from account.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username',) # Включаем только поле username

class AuthorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authors
        fields = "__all__"


class ArticlesSerializer(serializers.ModelSerializer):
    user = UserSerializer() # Используем созданный сериализатор для поля user
    moderator = UserSerializer() # Используем созданный сериализатор для поля moderator
    authors = AuthorsSerializer(read_only=True, many=True)

    class Meta:
        model = Articles
        # fields = "__all__"
        fields = (
            'id', 'title', 'annotation', 'description', 
            'status', 'review', 'user', 'moderator', 
            'creation_date', 'approving_date', 'publication_date',
            'authors'
        )


