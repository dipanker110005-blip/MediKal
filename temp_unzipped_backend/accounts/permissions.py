from rest_framework import permissions

class IsPatient(permissions.BasePermission):
    """
    Allows access only to users with the PATIENT role.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'PATIENT'

class IsDoctor(permissions.BasePermission):
    """
    Allows access only to users with the DOCTOR role.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'DOCTOR'

class IsAdmin(permissions.BasePermission):
    """
    Allows access to users with the ADMIN role, or Django superusers/staff.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.role == 'ADMIN' or request.user.is_staff)
