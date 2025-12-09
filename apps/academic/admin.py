# academic/admin.py
from django.contrib import admin
from .models import Program, Course, Lecture, Attendance, Assessment, Grade, Transcript

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'total_credits', 'last_synced')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'program', 'credit_hours')
    filter_horizontal = ('prerequisites',)

@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('course', 'date', 'start_time', 'end_time', 'faculty', 'is_makeup')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('lecture', 'student', 'checked_in', 'check_in_time', 'participation_score')

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('course', 'name', 'max_marks', 'weightage', 'date')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'student', 'marks_obtained', 'entered_at')

@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    list_display = ('student', 'gpa', 'verified', 'created_at')
