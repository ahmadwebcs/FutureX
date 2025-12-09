import uuid
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail

class Program(models.Model):
    program_id = models.CharField(max_length=50, unique=True)  # e.g., 'CS101'
    program_name = models.CharField(max_length=100)
    cutoff_score = models.FloatField()
    base_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.program_name

class Faculty(models.Model):
    faculty_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class Applicant(models.Model):
    STATUS_CHOICES = [
        ('In Progress', 'In Progress'),
        ('Eligible', 'Eligible'),
        ('Not Eligible', 'Not Eligible'),
        ('Admitted', 'Admitted'),
    ]
    applicant_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    cnic = models.CharField(max_length=15, unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    program_applied = models.ForeignKey(Program, on_delete=models.CASCADE)
    application_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='In Progress')
    merit_score = models.FloatField(null=True, blank=True)
    eligibility_status = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.applicant_id}"

class ApplicationDocument(models.Model):
    VERIFICATION_CHOICES = [
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    ]
    document_id = models.AutoField(primary_key=True)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50)  # e.g., 'transcript', 'cnic', 'photo'
    file_url = models.URLField()
    upload_date = models.DateTimeField(default=timezone.now)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='Pending')
    verified_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.document_type} - {self.applicant.name}"

class Scholarship(models.Model):
    STATUS_CHOICES = [
        ('Pending Approval', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    scholarship_id = models.AutoField(primary_key=True)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    waiver_percentage = models.IntegerField()  # 0-100
    scholarship_type = models.CharField(max_length=50)  # e.g., 'Full Scholarship'
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending Approval')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.scholarship_type} - {self.applicant.name}"

class InterviewSchedule(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    interview_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    interviewer = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')

    def __str__(self):
        return f"Interview {self.interview_id}"

class Section(models.Model):
    section_id = models.CharField(max_length=50, unique=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    semester_no = models.IntegerField()
    section_name = models.CharField(max_length=50)
    available_seats = models.IntegerField(default=0)

    def __str__(self):
        return self.section_name

class Admission(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    admission_id = models.AutoField(primary_key=True)
    student_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    applicant = models.OneToOneField(Applicant, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True)
    admission_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return f"Admission {self.student_id}"

class StudentFee(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Overdue', 'Overdue'),
    ]
    invoice_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    student = models.ForeignKey(Admission, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Invoice {self.invoice_id}"

class EnrollmentRecord(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    enrollment_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Admission, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return f"Enrollment {self.enrollment_id}"

class Timetable(models.Model):
    timetable_id = models.AutoField(primary_key=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    # Add timetable details as needed, e.g., subject, day, time

    def __str__(self):
        return f"Timetable for {self.section}"

class Waitlist(models.Model):
    STATUS_CHOICES = [
        ('Waiting', 'Waiting'),
        ('Admitted', 'Admitted'),
    ]
    waitlist_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Admission, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    semester_no = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Waiting')

    def __str__(self):
        return f"Waitlist {self.waitlist_id}"
