
from rest_framework import viewsets, generics, permissions, response, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
import csv

from . import perms
from .paginators import CoursePaginator
from .perms import IsOwnerOrReadOnly
from .serializers import CourseSerializer, UserSerializer, StudyClassSerializer, StudyClassSerializerForUserOutCourse, \
    PostSerializer, CommentSerializer, ResultLearningSerializer, ScoreColumnSerializer, SemesterSerializer, \
    StudyClassSerializerForGetStudyClass, PostSerializerForGetPost, ScoreInputSerializer
from .models import Course, User, StudyClass, Post, Comment, ResultLearning, ScoreColumn, Semester
from  rest_framework.decorators import action
from reportlab.pdfgen import canvas


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

    @action(detail=True, methods=['get'], url_name='get_studyclass')
    def get_studyclass(self, request, pk=None):
        user = self.get_object()
        # Đối với giáo viên, lấy lớp học mà họ dạy
        if user.role == User.UserRole.TEACHER:
            study_classes_as_teacher = StudyClass.objects.filter(teacher=user, active=True)
            serializer = StudyClassSerializerForGetStudyClass(study_classes_as_teacher, many=True)
        # Đối với sinh viên, lấy lớp học mà họ tham gia
        elif user.role == User.UserRole.STUDENT:
            study_classes_as_student = StudyClass.objects.filter(students=user, active=True)
            serializer = StudyClassSerializerForGetStudyClass(study_classes_as_student, many=True)
        else:
            return Response({"error": "User không phải là giáo viên hoặc sinh viên trong bất kỳ lớp học nào."},
                            status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.data, status=status.HTTP_200_OK)

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
    permission_classes = [permissions.IsAuthenticated]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(active=True).all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ['add_comment']:
            permission_classes = [permissions.IsAuthenticated, perms.UserinClassForCmt]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    @action(methods=['post'], url_path='add_comment', detail=True)
    def add_comment(self, request, pk):
        p = Comment.objects.create(user_comment=request.user, post=self.get_object(),
                                   content=request.data.get('content'))
        return Response(CommentSerializer(p).data, status=status.HTTP_201_CREATED)

    @action(methods=['get'], url_path='get_comments', detail=True)
    def get_comments(self, request, pk):
        comments = self.get_object().comments.filter(active=True).all()

        return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK)
class StudyClassViewSet(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = StudyClass.objects.filter(active=True).all()
    serializer_class = StudyClassSerializer
    permissions_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ['add_post']:
            permission_classes = [permissions.IsAuthenticated, perms.UserinClassForPost]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=True, url_path='export_grades')
    def export_grades(self, request, pk=None):
        # In ra toàn bộ query params để debug
        print("All query parameters:", request.query_params)

        study_class = self.get_object()
        if request.user != study_class.teacher:
            return Response({"message": "Bạn không có quyền xuất bảng điểm cho lớp học này."},
                            status=status.HTTP_403_FORBIDDEN)

        result_learnings = study_class.resultlearning_as_studyClass.all()
        file_format = request.query_params.get('format', 'csv')
        print("Chosen format:", file_format)

        print("Chosen format:", file_format)  # Debug để xem giá trị của format

        if file_format == 'pdf':
            return self.generate_pdf(result_learnings)
        else:
            return self.generate_csv(result_learnings, study_class)

    def generate_csv(self, result_learnings, study_class):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{study_class.name}_grades.csv"'

        writer = csv.writer(response)
        # Thêm các tiêu đề cột cho ScoreColumns
        header_row = ['Học Sinh', 'Điểm Giữa Kỳ', 'Điểm Cuối Kỳ']
        #  lấy mẫu từ đầu tiên
        if result_learnings:
            sample_result = result_learnings.first()
            score_columns = sample_result.score_columns.all()
            for sc in score_columns:
                header_row.append(sc.name_column)
        writer.writerow(header_row)

        for result in result_learnings:
            row = [
                result.student.get_full_name(),
                result.midterm_score,
                result.final_score,
            ]
            # Thêm điểm từ các ScoreColumn
            for sc in result.score_columns.all():
                row.append(sc.score)
            writer.writerow(row)

        return response

    def generate_pdf(self, result_learnings):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="grades.pdf"'

        p = canvas.Canvas(response)
        y = 800  # Vị trí Y bắt đầu
        # Thêm tiêu đề
        p.drawString(100, y, "Học Sinh - Điểm Giữa Kỳ - Điểm Cuối Kỳ - [Các ScoreColumn]")
        y -= 20

        for result in result_learnings:
            text = f"{result.student.get_full_name()} - {result.midterm_score} - {result.final_score}"
            # Thêm điểm từ các ScoreColumn vào cuối chuỗi
            for sc in result.score_columns.all():
                text += f" - {sc.name_column}: {sc.score}"
            p.drawString(100, y, text)
            y -= 20  # Di chuyển xuống dòng tiếp theo

            if y < 100:  # Kiểm tra nếu y quá thấp, tạo trang mới
                p.showPage()
                y = 800

        p.showPage()
        p.save()
        return response
    # /studyclass/{id_lớp_học}/export_grades?format=csv hoặc /studyclass/{id_lớp_học}/export_grades?format=pdf


    @action(methods=['get'], detail=True, url_path='get_result_learning')
    def get_result_learning(self, request, pk):
        resultLearning = self.get_object().resultlearning_as_studyClass.filter(active=True).all()

        return Response(ResultLearningSerializer(resultLearning, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='get_student_results')
    def get_student_results(self, request, pk=None):
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response({"error": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        study_class = self.get_object()
        try:
            student = study_class.students.get(id=student_id)
        except User.DoesNotExist:
            return Response({"error": "Student not found in this class."}, status=status.HTTP_404_NOT_FOUND)

        result_learnings = study_class.resultlearning_as_studyClass.filter(student=student)

        serializer = ResultLearningSerializer(result_learnings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    @action(methods=['get'], detail=True, url_path='get_teacher')
    def get_teacher(self, request, pk):
        # Lấy đối tượng StudyClass dựa trên khóa chính (pk) được cung cấp.
        study_class = self.get_queryset().get(pk=pk)
        # Lấy thông tin giáo viên thông qua trường 'teacher'.
        teacher = study_class.teacher

        # Serialize thông tin của giáo viên.
        serializer = UserSerializer(teacher, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='get_sudents')
    def get_students(self, request, pk):
        # Lấy đối tượng class hiện tại
        study_class = self.get_queryset().get(pk=pk)
        # Sử dụng related_name `classrooms_as_student` để truy vấn các học sinh.
        students = study_class.students.filter(classrooms_as_student__active=True).distinct()

        # Serialize thông tin của học sinh.
        serializer = UserSerializer(students, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True,  url_path='get_post')
    def get_post(self, request, pk):
        posts = self.get_object().post_as_studyclass.filter(active=True).all()

        return Response(PostSerializerForGetPost(posts, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='add_post', detail=True)
    def add_post(self, request, pk):
        p = Post.objects.create(user_post=request.user, class_study=self.get_object(), content=request.data.get('content'), title=request.data.get('title'))
        return Response(PostSerializer(p).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='input_scores')
    def input_scores(self, request, pk=None):
        study_class = self.get_object()
        scores_data = request.data.get('scores')

        for score_data in scores_data:
            serializer = ScoreInputSerializer(data=score_data, context={'request': request, 'study_class': study_class})
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Scores successfully inputted."}, status=status.HTTP_200_OK)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    # permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    permission_classes = [permissions.AllowAny]


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
            post=parent_comment.post
        )
        return Response(CommentSerializer(reply).data, status=status.HTTP_201_CREATED)




class ResultLearningViewSet(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = ResultLearning.objects.filter(active=True).all()
    serializer_class = ResultLearningSerializer


class ScoreColumnViewSet(viewsets.ModelViewSet, generics.RetrieveAPIView):
    queryset = ScoreColumn.objects.filter(active=True).all()
    serializer_class = ScoreColumnSerializer


class SemesterViewSet(viewsets.ModelViewSet, generics.RetrieveAPIView):
    queryset = Semester.objects.filter(active=True).all()
    serializer_class = SemesterSerializer

    @action(methods=['get'], detail=True, url_path='get_studyclass')
    def get_studyclass(self, request, pk):
        studycalass = self.get_object().classrooms_as_semester.filter(active=True).all()

        return Response(StudyClassSerializer(studycalass, many=True).data, status=status.HTTP_200_OK)
