from django.urls import path, include
from rest_framework.routers import DefaultRouter 
from . import views


router = DefaultRouter()
router.register('MonHoc', views.CourseViewSet, basename='courses')
router.register('User', views.UserViewSet)
router.register('StudyClass', views.StudyClassViewSet)


urlpatterns = [
    path('', include(router.urls))
]
