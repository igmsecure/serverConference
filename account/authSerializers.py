from rest_framework import serializers
from . models import CustomUser

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'password')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = CustomUser.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

class RefreshTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)