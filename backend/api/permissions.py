from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in ['GET', 'POST']


class Subscribepermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in ['GET', 'POST', 'DELETE']
