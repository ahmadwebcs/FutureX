from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'programs', views.ProgramViewSet)
router.register(r'faculty', views.FacultyViewSet)
router.register(r'applicants', views.ApplicantViewSet)
router.register(r'documents', views.ApplicationDocumentViewSet)
router.register(r'scholarships', views.ScholarshipViewSet)
router.register(r'interviews', views.InterviewScheduleViewSet)
router.register(r'sections', views.SectionViewSet)
router.register(r'admissions', views.AdmissionViewSet)
router.register(r'fees', views.StudentFeeViewSet)
router.register(r'enrollments', views.EnrollmentRecordViewSet)
router.register(r'timetables', views.TimetableViewSet)
router.register(r'waitlist', views.WaitlistViewSet)

urlpatterns = [
    path('create-applicant/', views.CreateApplicantProfile.as_view(), name='create_applicant'),
    path('upload-documents/', views.UploadDocuments.as_view(), name='upload_documents'),
    path('verify-documents/', views.RunDocumentVerification.as_view(), name='verify_documents'),
    path('evaluate-eligibility/', views.EvaluateEligibility.as_view(), name='evaluate_eligibility'),
    path('recommend-scholarship/', views.RecommendScholarship.as_view(), name='recommend_scholarship'),
    path('schedule-interview/', views.ScheduleInterview.as_view(), name='schedule_interview'),
    path('finalize-admission/', views.FinalizeAdmission.as_view(), name='finalize_admission'),
    path('create-fee-record/', views.CreateFeeRecord.as_view(), name='create_fee_record'),
    path('assign-section/', views.AssignSectionAndTimetable.as_view(), name='assign_section'),
    path('generate-report/', views.AdmissionReportGenerator.as_view(), name='generate_report'),
]

# Add router URLs
urlpatterns += router.urls
