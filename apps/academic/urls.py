# academic/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (ProgramViewSet, CourseViewSet, LectureViewSet,
                    AttendanceViewSet, AssessmentViewSet, GradeViewSet, TranscriptViewSet)

router = DefaultRouter()
router.register('programs', ProgramViewSet)
router.register('courses', CourseViewSet)
router.register('lectures', LectureViewSet)
router.register('attendances', AttendanceViewSet)
router.register('assessments', AssessmentViewSet)
router.register('grades', GradeViewSet)
router.register('transcripts', TranscriptViewSet)

urlpatterns = [
    path('api/academic/', include(router.urls)),
]
