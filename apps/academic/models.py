# academic/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Program(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, unique=True)
    total_credits = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    last_synced = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Course(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, unique=True)
    credit_hours = models.PositiveSmallIntegerField()
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='dependent_courses')

    def __str__(self):
        return f"{self.code} - {self.name}"

class Lecture(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lectures')
    faculty = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                limit_choices_to={'is_staff': True})
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=150, blank=True)
    is_makeup = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.course.code} @ {self.date} {self.start_time}-{self.end_time}"

class Attendance(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances',
                                limit_choices_to={'is_staff': False})
    checked_in = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(null=True, blank=True)
    participation_score = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('lecture', 'student')

    def __str__(self):
        return f"Attendance: {self.student} - {self.lecture} - {self.checked_in}"

class Assessment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    name = models.CharField(max_length=120)
    max_marks = models.FloatField()
    weightage = models.FloatField(help_text="percentage of course grade (0-100)")
    date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.code} - {self.name}"

class Grade(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='grades')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades',
                                limit_choices_to={'is_staff': False})
    marks_obtained = models.FloatField()
    entered_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('assessment', 'student')

    def __str__(self):
        return f"{self.student} - {self.assessment} - {self.marks_obtained}"

class Transcript(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transcripts',
                                limit_choices_to={'is_staff': False})
    gpa = models.FloatField(default=0.0)
    data = models.JSONField(default=dict)  # store snapshot of courses/grades
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified = models.BooleanField(default=False)
    blockchain_hash = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return f"Transcript({self.student}) GPA={self.gpa}"
