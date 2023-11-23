from rest_framework import serializers

from .models import *


class AuthorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authors
        fields = "__all__"


class ArticlesSerializer(serializers.ModelSerializer):
    authors = AuthorsSerializer(read_only=True, many=True)

    class Meta:
        model = Articles
        # fields = "__all__"
        fields = (
            'id', 'title', 'annotation', 'description', 
            'status', 'user', 'moderator', 
            'creation_date', 'approving_date', 'publication_date',
            'authors'
        )


