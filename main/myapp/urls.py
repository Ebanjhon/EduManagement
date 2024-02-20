from django.urls import path, include
from rest_framework.routers import DefaultRouter 
from . import views


router = DefaultRouter()
router.register('Course', views.CourseViewSet, basename='courses')
router.register('User', views.UserViewSet)
router.register('StudyClass', views.StudyClassViewSet)
router.register('Post', views.PostViewSet,  basename='Post')
router.register('Comments', views.CommentViewSet, basename='comments')
router.register('ResultLearning', views.ResultLearningViewSet, basename='ResultLearning')
router.register('ScoreColumn', views.ScoreColumnViewSet, basename='ScoreColumn')







urlpatterns = [
    path('', include(router.urls))
]
