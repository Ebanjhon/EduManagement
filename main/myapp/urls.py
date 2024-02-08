from django.urls import path, include
from rest_framework.routers import DefaultRouter 
from . import views


router = DefaultRouter()
router.register('MonHoc', views.CourseViewSet, basename='courses')
router.register('user', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls))
]
