

from rest_framework.permissions import BasePermission

#تحديد صلاحيات المدير


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "admin"
    
#تحديد صلاحيات الطفل

class IsChild(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "child"