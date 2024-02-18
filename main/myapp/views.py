from rest_framework import viewsets, generics, permissions, response
from rest_framework.response import Response

from .paginators import CoursePaginator
from .serializers import CourseSerializer, UserSerializer, StudyClassSerializer, StudyClassSerializerForUserOutCourse
from .models import Course, User, StudyClass
from  rest_framework.decorators import action


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView):
# class UserViewSet(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        user = self.get_object()
        # Lấy tất cả lớp học mà user này là sinh viên
        study_classes = StudyClass.objects.filter(students=user)
        serializer = StudyClassSerializerForUserOutCourse(study_classes, many=True)
        return Response(serializer.data)



class CourseViewSet(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = Course.objects.filter(active=True).all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator
    # permission_classes = [permissions.IsAuthenticated]

class StudyClassViewSet(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = StudyClass.objects.filter(active=True).all()
    serializer_class = StudyClassSerializer

