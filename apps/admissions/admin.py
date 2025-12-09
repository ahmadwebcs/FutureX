from django.contrib import admin
from apps.admissions.models import Program, Faculty, Applicant, ApplicationDocument, Scholarship, InterviewSchedule, Section, Admission, StudentFee, EnrollmentRecord, Timetable, Waitlist

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['id', 'program_id', 'program_name', 'cutoff_score', 'base_fee']

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['id', 'faculty_id', 'name', 'email']

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ['id', 'applicant_id', 'name', 'email', 'cnic', 'program_applied', 'status']

@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ['document_id', 'applicant', 'document_type', 'verification_status']

@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ['scholarship_id', 'applicant', 'waiver_percentage', 'scholarship_type', 'status']

@admin.register(InterviewSchedule)
class InterviewScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'interview_id', 'applicant', 'interviewer', 'date_time', 'status']

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'section_id', 'program', 'semester_no', 'section_name', 'available_seats']

@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ['admission_id', 'student_id', 'applicant', 'program', 'status']

@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice_id', 'student', 'total_amount', 'status']

@admin.register(EnrollmentRecord)
class EnrollmentRecordAdmin(admin.ModelAdmin):
    list_display = ['enrollment_id', 'student', 'section', 'status']

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['timetable_id', 'section']

@admin.register(Waitlist)
class WaitlistAdmin(admin.ModelAdmin):
    list_display = ['waitlist_id', 'student', 'program', 'status']

# Register your models here.
