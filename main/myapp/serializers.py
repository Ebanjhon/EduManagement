from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
from .models import User, StudyClass, Semester, ScoreColumn, ResultLearning, Course, Post, Comment


class UserSerializer(serializers.ModelSerializer):
    # Trường mới để tải lên avatar, không hiển thị trong phản hồi API (write_only=True)
    upload_avatar = serializers.ImageField(write_only=True, required=False)
    # SerializerMethodField để trả lại URL avatar
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, User):
        request = self.context.get('request')
        if User.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri('/static/%s' % User.avatar.name)
            return '/static/%s' % User.avatar.name

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'avatar', 'upload_avatar', 'role', 'birth_date', 'address']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        """
        Kiểm tra định dạng email.
        """
        if not value.endswith('@ou.edu.vn'):
            raise serializers.ValidationError("Email không thuộc OU.edu VD: truongdaihocmo@ou.edu.vn")
        return value

    def create(self, validated_data):
        avatar_data = validated_data.pop('upload_avatar', None)
        user = User.objects.create_user(**validated_data)
        if avatar_data:
            user.avatar = avatar_data
        user.set_password(validated_data['password'])
        user.save()
        return user

class CourseSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(source='image')


    def get_image(self, Course):
        request = self.context.get('request')
        if Course.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri('/static/%s' % Course.image.name)
            return '/static/%s' % Course.image.name

    class Meta:
        model = Course
        fields = '__all__'
class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'
class StudyClassSerializer(serializers.ModelSerializer):
    semester = SemesterSerializer()  # Sử dụng SemesterSerializer
    teacher = UserSerializer()  # Sử dụng UserSerializer cho giáo viên
    students = UserSerializer(many=True)  # Sử dụng UserSerializer cho sinh viên, nhớ thêm many=True
    course = CourseSerializer()
    class Meta:
        model = StudyClass
        fields = ['id', 'name', 'semester', 'teacher', 'students', 'course']
# dành cho lấy tất cả khóa học mà sinh viên học


class StudyClassSerializerForGetStudyClass(serializers.ModelSerializer):
    semester = SemesterSerializer()  # Sử dụng SemesterSerializer
    course = CourseSerializer()

    class Meta:
        model = StudyClass
        fields = ['id', 'name', 'semester', 'course']  # Loại bỏ 'students' từ fields


class StudyClassSerializerForUserOutCourse(serializers.ModelSerializer):
    course = CourseSerializer()
    class Meta:
        model = StudyClass
        fields = [ 'course']



class PostSerializer(serializers.ModelSerializer):
    user_post = UserSerializer()
    class_study = StudyClassSerializer()
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'user_post', 'class_study']


class PostSerializerForGetPost(serializers.ModelSerializer):
    user_post = UserSerializer()
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'user_post']
class CommentSerializer(serializers.ModelSerializer):
    user_comment = UserSerializer(read_only=True)
    comment_child = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'

    def get_comment_child(self, obj):
        # Lấy tất cả các comment con liên quan đến comment hiện tại
        replies = obj.replies.all()
        # Serialize các comment con
        return CommentSerializer(replies, many=True, context=self.context).data

class ScoreColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreColumn
        fields = ['id', 'name_column', 'score', 'result_learning']

class ResultLearningSerializer(serializers.ModelSerializer):
    score_columns = ScoreColumnSerializer(many=True, read_only=True)
    class Meta:
        model = ResultLearning
        fields = ['midterm_score', 'final_score', 'score_columns', 'study_class', 'student']


class ScoreColumnInputSerializer(serializers.Serializer):
    column_name = serializers.CharField(max_length=50)
    score = serializers.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)])

class ScoreInputSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    midterm_score = serializers.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    final_score = serializers.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    score_columns = ScoreColumnInputSerializer(many=True)

    def create(self, validated_data):
        student_id = validated_data.get('student_id')
        midterm_score = validated_data.get('midterm_score')
        final_score = validated_data.get('final_score')
        score_columns_data = validated_data.get('score_columns')

        # Sửa đổi ở đây: Thay thế Student bằng User
        student = User.objects.get(id=student_id)  # Sử dụng User thay vì Student không định nghĩa
        study_class = self.context['study_class']

        # Tạo hoặc cập nhật ResultLearning
        result_learning, created = ResultLearning.objects.update_or_create(
            student=student,
            study_class=study_class,
            defaults={'midterm_score': midterm_score, 'final_score': final_score}
        )

        # Tạo hoặc cập nhật các ScoreColumn
        for column_data in score_columns_data:
            column_name = column_data['column_name']
            score = column_data['score']
            ScoreColumn.objects.update_or_create(
                result_learning=result_learning,
                name_column=column_name,  # Đảm bảo tên trường khớp với model
                defaults={'score': score}
            )

        return result_learning
