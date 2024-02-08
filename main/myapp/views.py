from rest_framework import viewsets, generics, permissions
from .serializers import CourseSerializer, UserSerializer
from .models import Course, User


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView):
# class UserViewSet(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer



class CourseViewSet(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # permission_classes = [permissions.IsAuthenticated]