from rest_framework import permissions

class OwnerAuthenticated(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view) and request.user == obj.user_post
# chi nguoi tron lop
class UserinClassForCmt(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.class_study.teacher:
            return True
        if request.user in obj.class_study.students.all():
            return True
        return False

class UserinClassForPost(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.teacher:
            return True
        if request.user in obj.students.all():
            return True
        return False
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user_comment == request.user


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'

class IsTeacherUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'teacher'

class IsStudentUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'student'