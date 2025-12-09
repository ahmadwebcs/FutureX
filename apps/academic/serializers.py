# academic/serializers.py
from rest_framework import serializers
from .models import Program, Course, Lecture, Attendance, Assessment, Grade, Transcript
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    program = ProgramSerializer(read_only=True)
    program_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Program.objects.all(), source='program')

    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'credit_hours', 'program', 'program_id', 'prerequisites']

class LectureSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Course.objects.all(), source='course')
    faculty = UserSimpleSerializer(read_only=True)
    faculty_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.filter(is_staff=True), source='faculty', required=False, allow_null=True)

    class Meta:
        model = Lecture
        fields = ['id', 'course', 'course_id', 'faculty', 'faculty_id', 'date', 'start_time', 'end_time', 'location', 'is_makeup']

class AttendanceSerializer(serializers.ModelSerializer):
    lecture = LectureSerializer(read_only=True)
    lecture_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Lecture.objects.all(), source='lecture')
    student = UserSimpleSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.filter(is_staff=False), source='student')

    class Meta:
        model = Attendance
        fields = ['id', 'lecture', 'lecture_id', 'student', 'student_id', 'checked_in', 'check_in_time', 'participation_score']

class AssessmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Course.objects.all(), source='course')

    class Meta:
        model = Assessment
        fields = ['id', 'course', 'course_id', 'name', 'max_marks', 'weightage', 'date']

class GradeSerializer(serializers.ModelSerializer):
    assessment = AssessmentSerializer(read_only=True)
    assessment_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Assessment.objects.all(), source='assessment')
    student = UserSimpleSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.filter(is_staff=False), source='student')

    class Meta:
        model = Grade
        fields = ['id', 'assessment', 'assessment_id', 'student', 'student_id', 'marks_obtained', 'entered_at']

class TranscriptSerializer(serializers.ModelSerializer):
    student = UserSimpleSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.filter(is_staff=False), source='student')

    class Meta:
        model = Transcript
        fields = ['id', 'student', 'student_id', 'gpa', 'data', 'created_at', 'updated_at', 'verified', 'blockchain_hash']
