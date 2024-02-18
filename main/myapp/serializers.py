from rest_framework import serializers
from .models import User, StudyClass, Semester, ScoreColumn, ResultLearning, Course


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']
        # fields = '__all__'

    # ghi de bam mat khau
    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        return user


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'
class StudyClassSerializer(serializers.ModelSerializer):

    course = CourseSerializer()
    class Meta:
        model = StudyClass
        fields = ['id', 'name', 'semester', 'teacher', 'students', 'course']

