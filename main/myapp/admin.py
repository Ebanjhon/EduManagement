from django.contrib import admin
from .models import User, StudyClass, Semester, ScoreColumn, ResultLearning, Course

admin.site.register(User)
admin.site.register(ScoreColumn)
admin.site.register(StudyClass)
admin.site.register(Semester)
admin.site.register(ResultLearning)
admin.site.register(Course)
# admin.site.register(StudyClass)
