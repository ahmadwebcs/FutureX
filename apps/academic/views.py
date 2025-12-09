# academic/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Program, Course, Lecture, Attendance, Assessment, Grade, Transcript
from .serializers import (ProgramSerializer, CourseSerializer, LectureSerializer,
                          AttendanceSerializer, AssessmentSerializer, GradeSerializer, TranscriptSerializer)
from django.db.models import Avg

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('program').all()
    serializer_class = CourseSerializer

class LectureViewSet(viewsets.ModelViewSet):
    queryset = Lecture.objects.select_related('course', 'faculty').all()
    serializer_class = LectureSerializer

    @action(detail=True, methods=['get'])
    def attendances(self, request, pk=None):
        lecture = self.get_object()
        qs = lecture.attendances.select_related('student')
        serializer = AttendanceSerializer(qs, many=True)
        return Response(serializer.data)

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('lecture', 'student').all()
    serializer_class = AttendanceSerializer

class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.select_related('course').all()
    serializer_class = AssessmentSerializer

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.select_related('assessment', 'student').all()
    serializer_class = GradeSerializer

    @action(detail=False, methods=['get'])
    def student_summary(self, request):
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response({'detail': 'student_id query param required'}, status=status.HTTP_400_BAD_REQUEST)
        qs = Grade.objects.filter(student_id=student_id).select_related('assessment__course')
        avg = qs.aggregate(average=Avg('marks_obtained'))['average']
        serializer = GradeSerializer(qs, many=True)
        return Response({'average': avg, 'grades': serializer.data})

class TranscriptViewSet(viewsets.ModelViewSet):
    queryset = Transcript.objects.select_related('student').all()
    serializer_class = TranscriptSerializer
