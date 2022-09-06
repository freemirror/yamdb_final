from rest_framework import permissions


class SpecialPermission(permissions.BasePermission):
    """Доступ для чтения всем пользователям,
    доступ на создание для аутентифицированного пользователя,
    доступ для изменения или удаления у автора, модератора и админа.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
            or request.user.is_superuser
        )


class AdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )


class ReadAnyWriteAdmin(permissions.BasePermission):

    def has_permission(self, request, view):

        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )
