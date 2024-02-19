
from rest_framework import viewsets, generics, permissions, response, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import perms
from .paginators import CoursePaginator
from .perms import IsOwnerOrReadOnly
from .serializers import CourseSerializer, UserSerializer, StudyClassSerializer, StudyClassSerializerForUserOutCourse, \
    PostSerializer, CommentSerializer
from .models import Course, User, StudyClass, Post, Comment
from  rest_framework.decorators import action


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        user = self.get_object()
        # Lấy tất cả lớp học mà user này là sinh viên
        study_classes = StudyClass.objects.filter(students=user)
        serializer = StudyClassSerializerForUserOutCourse(study_classes, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        if self.action.__eq__('current_user'):
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], url_name='current-user', detail=False)
    def current_user(self, request):
        return Response(UserSerializer(request.user).data)

class CourseViewSet(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = Course.objects.filter(active=True).all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator
    # permission_classes = [permissions.IsAuthenticated]


class PostViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [perms.OwnerAuthenticated]

    def get_permissions(self):
        if self.action in ['add_coment']:
            return [permissions.IsAuthenticated()]
        return self.serializer_class

    @action(methods=['post'], url_path='add_coment', detail=True)
    def add_coment(self, request, pk):
        p = Comment.objects.create(user_comment=request.user, post=self.get_object(),
                                content=request.data.get('content'))
        return Response(CommentSerializer(p).data, status=status.HTTP_201_CREATED)
class StudyClassViewSet(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = StudyClass.objects.filter(active=True).all()
    serializer_class = StudyClassSerializer
    permissions_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ['add_post']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]



    @action(methods=['post'], url_path='add_post', detail=True)
    def add_post(self, request, pk):
        p = Post.objects.create(user_post=request.user, class_study=self.get_object(), content=request.data.get('content'))
        return Response(PostSerializer(p).data, status=status.HTTP_201_CREATED)
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]

    def perform_create(self, serializer):
        # Tự động thêm user đăng nhập vào làm người tạo comment
        serializer.save(user_comment=self.request.user)

    @action(detail=True, methods=['post'])
    def add_reply(self, request, pk=None):
        parent_comment = self.get_object()
        comment = self.get_object()
        reply_content = request.data.get('content')
        reply = Comment.objects.create(
            content=reply_content,
            parent_comment=comment,
            user_comment=request.user,
            post = parent_comment.post
        )
        return Response(CommentSerializer(reply).data, status=status.HTTP_201_CREATED)
