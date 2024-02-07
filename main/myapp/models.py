from django.contrib.auth.models import AbstractUser
from django.db import models


#class tai khoan
class User(AbstractUser):
    class UserRole(models.TextChoices):
        ADMIN = 'admin'
        TEACHER = 'teacher'
        STUDENT = 'student'
        
    role = models.CharField(max_length=10, choices=UserRole.choices, default=UserRole.STUDENT)
    id_user = models.IntegerField(unique=False, blank=True, null=True)
    birth_date = models.DateField(null=True)
    address = models.CharField(max_length=128, null=True)
    avatar = models.ImageField(upload_to='avatar/%Y/%m', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding and self.id_user is None:
            count = User.objects.filter(role=self.role).count()
            self.id_user = count + 1
        super(User, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.first_name +" "+ self.last_name


# cac models khac 
#class truu tuong
class ModelBase(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now = True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True


#class hoc ky
class Semester(ModelBase):
    schoolyear = models.CharField(max_length=10, null = False, unique=True)

    def __str__(self):
        return self.schoolyear
    
#class mon hoc
class Course(ModelBase):
    name = models.CharField(max_length=100, unique=True, null=False)
    credit_hours = models.CharField(max_length=10, null=True)
    def __str__(self):
        return self.name
    
#class lop hoc
class StudyClass(ModelBase):
    name = models.CharField(max_length=100, unique=False, null=False)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)#nam hoc ky
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classrooms_as_teacher', limit_choices_to={'role': User.UserRole.TEACHER})
    students = models.ManyToManyField(User, related_name='classrooms_as_student', limit_choices_to={'role': User.UserRole.STUDENT})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
#class ket qua hoc tap
class ResultLearning(ModelBase):
    midterm_score = models.FloatField()
    final_score = models.FloatField()
    is_draft = models.BooleanField(default=True)#Dùng để check xem đa luu chua
    study_class = models.ForeignKey(StudyClass, on_delete=models.CASCADE, null=True)#lop hoc
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resultlearning_as_student', 
                                limit_choices_to={'role': User.UserRole.STUDENT},
                                null=True)

    def __str__(self):
        return self.student.get_full_name() + " " + self.study_class.name
    

#class cot diem cong
class ScoreColumn(ModelBase):
    name_column = models.CharField(max_length = 50, null = False)
    score = models.FloatField()
    result_learning = models.ForeignKey(ResultLearning, on_delete=models.CASCADE)#ket qua hoc tap