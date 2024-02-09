from django.contrib import admin
from django.utils.html import format_html

from .models import User, StudyClass, Semester, ScoreColumn, ResultLearning, Course, Post, Comment

class UserAdmin(admin.ModelAdmin):
    list_display = ["id","id_user", "username", "first_name", "last_name", "role", "avatar_image"]
    search_fields = ["id_user", "username"]
    list_filter = ["role"]

    def avatar_image(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="width: auto; height: 80px; object-fit: contain;" />', obj.avatar.url)
        else:
            return "No Image"

    avatar_image.short_description = 'Avatar'

class ResultLearningAdmin(admin.ModelAdmin):
    list_display = ["student", "study_class", "midterm_score", "final_score"]
    search_fields = ('student__first_name', 'student__last_name', 'study_class__name')
    list_filter = ["study_class"]

class StudyClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'semester', 'teacher', 'course')
    search_fields = ('name', 'teacher__first_name', 'course__name')
    list_filter = ('semester', 'course', 'teacher')

class CourseAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "credit_hours"]
    search_fields = ["id", "name"]
    list_filter = ["name"]

class ScoreColumnAdmin(admin.ModelAdmin):
    list_display = ('name_column', 'display_student', 'score', 'display_result_learning')
    search_fields = ('name_column', 'result_learning__study_class__name', 'result_learning__student__first_name', 'result_learning__student__last_name')
    list_filter = ('result_learning__study_class', 'result_learning__student')

    def display_student(self, obj):
        # Trả về tên đầy đủ của sinh viên
        return obj.result_learning.student.get_full_name()
    display_student.short_description = 'Student'

    def display_result_learning(self, obj):
        # Trả về thông tin về lớp học và điểm
        study_class_name = obj.result_learning.study_class.name
        return f"{study_class_name}"
    display_result_learning.short_description = 'Class Information'

admin.site.register(User, UserAdmin)
admin.site.register(ScoreColumn, ScoreColumnAdmin)
admin.site.register(StudyClass, StudyClassAdmin)
admin.site.register(Semester)
admin.site.register(ResultLearning, ResultLearningAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Post)
admin.site.register(Comment)