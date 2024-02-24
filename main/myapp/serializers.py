from rest_framework import serializers
from .models import User, StudyClass, Semester, ScoreColumn, ResultLearning, Course, Post, Comment


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=True)  # Đây là trường để upload ảnh
    avatar_url = serializers.SerializerMethodField()  # Đây là trường để trả về URL đầy đủ của ảnh

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'avatar','avatar_url', 'role', 'birth_date',
                  'address']
        # fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def get_avatar_url(self, obj):
        """Trả về URL đầy đủ cho ảnh avatar."""
        request = self.context.get('request')
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri('/static/%s' % obj.avatar.name)
            return '/static/%s' % User.avatar.name

    # # avatar = serializers.SerializerMethodField(source='avatar')
    # avatar = serializers.ImageField(required=True)
    #
    # def get_avatar(self, User):
    #     request = self.context.get('request')
    #     if User.avatar:
    #         request = self.context.get('request')
    #         if request:
    #             return request.build_absolute_uri('/static/%s' % User.avatar.name)
    #         return '/static/%s' % User.avatar.name
    #
    # ghi de bam mat khau
    def validate_email(self, value):
        """
        Kiểm tra định dạng email.
        """
        if not value.endswith('@ou.edu.vn'):
            raise serializers.ValidationError("Email không thuộc OU.edu VD: truongdaihocmo@ou.edu.vn")
        return value

    def create(self, validated_data):
        """
                Tạo user với role mặc định là STUDENT và kiểm tra avatar.
                """
        validated_data['role'] = User.UserRole.STUDENT  # Thiết lập role mặc định là STUDENT
        # Thêm logic kiểm tra avatar tại đây nếu cần
        user = User.objects.create_user(**validated_data)
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
    class Meta:
        model = Post
        fields = ['id', 'title', 'content']
class CommentSerializer(serializers.ModelSerializer):
    user_comment = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'

class ScoreColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreColumn
        fields = ['id', 'name_column', 'score', 'result_learning']

class ResultLearningSerializer(serializers.ModelSerializer):
    score_columns = ScoreColumnSerializer(many=True, read_only=True)
    class Meta:
        model = ResultLearning
        fields = ['midterm_score', 'final_score', 'score_columns', 'study_class', 'student']