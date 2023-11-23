from rest_framework.permissions import BasePermission

from account.JWTConfig import getJwtPayload, getAccessToken
from account.models import CustomUser


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        token = getAccessToken(request)

        if token is None:
            return False

        # Ensure token is valid
        try:
            payload = getJwtPayload(token)
        except Exception as e:
            return False

        # Ensure user exists
        try:
            user = CustomUser.objects.get(pk=payload['user_id'])
        except Exception as e:
            return False

        return user.is_active


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        token = getAccessToken(request)

        if token is None:
            return False

        # Ensure token is valid
        try:
            payload = getJwtPayload(token)
        except Exception as e:
            return False

        # Ensure user exists
        try:
            user = CustomUser.objects.get(pk=payload['user_id'])
        except Exception as e:
            return False

        return user.is_moderator