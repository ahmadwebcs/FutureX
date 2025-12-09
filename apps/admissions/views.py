from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.core.mail import send_mail
from django.db import transaction
from .models import *
from .serializers import *
import uuid
from datetime import datetime, timedelta
import os

class CreateApplicantProfile(APIView):
    def post(self, request):
        data = request.data
        required_fields = ['name', 'email', 'cnic', 'program_applied']
        for field in required_fields:
            if field not in data or not data[field]:
                return Response({"error": f"Missing required field - {field}"}, status=status.HTTP_400_BAD_REQUEST)

        if Applicant.objects.filter(cnic=data['cnic']).exists() or Applicant.objects.filter(email=data['email']).exists():
            return Response({"error": "Duplicate application detected"}, status=status.HTTP_400_BAD_REQUEST)

        # Get program instance
        try:
            program = Program.objects.get(program_id=data['program_applied'])
        except Program.DoesNotExist:
            return Response({"error": "Invalid program ID"}, status=status.HTTP_400_BAD_REQUEST)

        applicant_id = str(uuid.uuid4())[:10].upper()  # Short unique ID
        applicant = Applicant.objects.create(
            applicant_id=applicant_id,
            name=data['name'],
            email=data['email'],
            cnic=data['cnic'],
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            program_applied=program,
            status='In Progress'
        )

        # Send email
        send_mail(
            'Application Created',
            f'Your application has been created successfully. ID: {applicant_id}',
            'no-reply@futurex.edu',
            [applicant.email],
            fail_silently=True,
        )

        # Log action (mock logging)
        print(f"Applicant profile created: {applicant_id}")

        return Response({"message": f"Application created successfully with ID: {applicant_id}"}, status=status.HTTP_201_CREATED)

class UploadDocuments(APIView):
    def post(self, request):
        applicant_id = request.data.get('applicant_id')
        document_list = request.data.get('document_list')  # List of dicts with type, size, name

        if not Applicant.objects.filter(applicant_id=applicant_id).exists():
            return Response({"error": "Invalid applicant ID"}, status=status.HTTP_400_BAD_REQUEST)

        applicant = Applicant.objects.get(applicant_id=applicant_id)

        for doc in document_list:
            file_size = doc['size']
            file_name = doc['name']

            if file_size > 10 * 1024 * 1024:  # 10MB
                return Response({"error": f"File too large ({file_name})"}, status=status.HTTP_400_BAD_REQUEST)

            valid_formats = ['jpg', 'png', 'pdf']
            extension = file_name.split('.')[-1].lower()
            if extension not in valid_formats:
                return Response({"error": f"Invalid file format for {file_name}"}, status=status.HTTP_400_BAD_REQUEST)

            # Mock file upload
            storage_path = f"/storage/admissions/docs/{applicant_id}/"
            file_url = f"{storage_path}{file_name}"

            ApplicationDocument.objects.create(
                applicant=applicant,
                document_type=doc['type'],
                file_url=file_url,
                verification_status='Pending'
            )

        # Run document verification (call the function)
        doc_verification_view = RunDocumentVerification()
        doc_verification_view.post(request._clone_with_data({'applicant_id': applicant_id}))

        print(f"Documents uploaded for applicant {applicant_id}")
        return Response({"message": "Documents uploaded successfully and sent for verification"}, status=status.HTTP_200_OK)

class RunDocumentVerification(APIView):
    def post(self, request):
        applicant_id = request.data.get('applicant_id')

        docs = ApplicationDocument.objects.filter(
            applicant__applicant_id=applicant_id,
            verification_status='Pending'
        )

        if not docs:
            return Response({"message": "No documents pending verification"}, status=status.HTTP_200_OK)

        for doc in docs:
            # Mock OCR
            text_data = self.mock_ocr(doc.file_url)
            verification_result = self.validate_text(text_data, doc.document_type)

            if verification_result:
                doc.verification_status = 'Verified'
                doc.verified_at = timezone.now()
            else:
                doc.verification_status = 'Rejected'
                doc.remarks = 'Data mismatch or unreadable'

            doc.save()

            print(f"Document verified: {doc.document_type} for {applicant_id}")

        # Update applicant verification status
        self.update_applicant_verification_status(applicant_id)

        return Response({"message": f"Document verification completed for applicant: {applicant_id}"}, status=status.HTTP_200_OK)

    def mock_ocr(self, file_url):
        # Mock OCR result
        if 'transcript' in file_url:
            return {'matric_marks': 85.0, 'inter_marks': 90.0}
        elif 'cnic' in file_url:
            return {'cnic': '1234567890123'}
        else:
            return {}

    def validate_text(self, text_data, doc_type):
        if doc_type == 'transcript':
            return 'matric_marks' in text_data and 'inter_marks' in text_data
        elif doc_type == 'cnic':
            return 'cnic' in text_data
        return False

    def update_applicant_verification_status(self, applicant_id):
        total_docs = ApplicationDocument.objects.filter(applicant__applicant_id=applicant_id).count()
        verified_docs = ApplicationDocument.objects.filter(applicant__applicant_id=applicant_id, verification_status='Verified').count()
        # Not implemented further

class EvaluateEligibility(APIView):
    def post(self, request):
        applicant_id = request.data.get('applicant_id')

        applicant = get_object_or_404(Applicant, applicant_id=applicant_id)
        verified_docs = ApplicationDocument.objects.filter(applicant=applicant, verification_status='Verified')

        if not verified_docs:
            return Response({"error": "Required documents not verified"}, status=status.HTTP_400_BAD_REQUEST)

        academic_records = {}
        for doc in verified_docs:
            if doc.document_type == 'transcript':
                academic_records = {'matric_marks': 85, 'inter_marks': 90}  # Mock

        matric_marks = academic_records.get('matric_marks', 0)
        inter_marks = academic_records.get('inter_marks', 0)

        merit_score = round((matric_marks * 0.4) + (inter_marks * 0.6), 2)
        cutoff = applicant.program_applied.cutoff_score

        if merit_score >= cutoff:
            eligibility_status = "Eligible"
        else:
            eligibility_status = "Not Eligible"

        applicant.merit_score = merit_score
        applicant.eligibility_status = eligibility_status
        applicant.save()

        # Recommend scholarship
        scholarship_view = RecommendScholarship()
        scholarship_view.post(request._clone_with_data({'applicant_id': applicant_id, 'merit_score': merit_score}))

        print(f"Eligibility evaluated for applicant {applicant_id}")
        return Response({"message": f"Applicant {eligibility_status} with Merit Score: {merit_score}"}, status=status.HTTP_200_OK)

class RecommendScholarship(APIView):
    def post(self, request):
        applicant_id = request.data.get('applicant_id')
        merit_score = request.data.get('merit_score')

        if merit_score >= 90:
            waiver = 100
            scholarship_type = "Full Scholarship"
        elif merit_score >= 80:
            waiver = 50
            scholarship_type = "Half Scholarship"
        elif merit_score >= 70:
            waiver = 25
            scholarship_type = "Partial Scholarship"
        else:
            waiver = 0
            scholarship_type = "No Scholarship"

        applicant = get_object_or_404(Applicant, applicant_id=applicant_id)

        scholarship = Scholarship.objects.create(
            applicant=applicant,
            waiver_percentage=waiver,
            scholarship_type=scholarship_type,
            status='Pending Approval'
        )

        # Send email
        send_mail(
            'Scholarship Recommendation',
            f'You have been recommended for a {scholarship_type} ({waiver}% waiver).',
            'no-reply@futurex.edu',
            [applicant.email],
            fail_silently=True,
        )

        print(f"Scholarship recommended for applicant {applicant_id}")
        return Response({"message": f"Scholarship recommendation: {scholarship_type} ({waiver}%)"}, status=status.HTTP_200_OK)

class ScheduleInterview(APIView):
    def post(self, request):
        data = request.data
        applicant_id = data.get('applicant_id')
        interviewer_id = data.get('interviewer_id')
        date_time_str = data.get('date_time')

        if not Applicant.objects.filter(applicant_id=applicant_id).exists():
            return Response({"error": "Invalid applicant ID"}, status=status.HTTP_400_BAD_REQUEST)

        if not Faculty.objects.filter(faculty_id=interviewer_id).exists():
            return Response({"error": "Invalid interviewer ID"}, status=status.HTTP_400_BAD_REQUEST)

        date_time = datetime.fromisoformat(date_time_str)
        # Mock availability check
        availability = True  # Assume available

        if not availability:
            return Response({"error": "Interviewer not available at this time"}, status=status.HTTP_400_BAD_REQUEST)

        interview_id = str(uuid.uuid4())[:10].upper()
        applicant = Applicant.objects.get(applicant_id=applicant_id)
        interviewer = Faculty.objects.get(faculty_id=interviewer_id)

        InterviewSchedule.objects.create(
            interview_id=interview_id,
            applicant=applicant,
            interviewer=interviewer,
            date_time=date_time,
            status='Scheduled'
        )

        # Send emails
        send_mail('Interview Scheduled', f'Your interview is scheduled on {date_time}.', 'no-reply@futurex.edu', [applicant.email], fail_silently=True)
        send_mail('New Interview Assigned', f'You have an interview with {applicant.name} on {date_time}.', 'no-reply@futurex.edu', [interviewer.email], fail_silently=True)

        print(f"Interview scheduled {interview_id}")
        return Response({"message": f"Interview scheduled successfully on {date_time}"}, status=status.HTTP_201_CREATED)

class FinalizeAdmission(APIView):
    def post(self, request):
        applicant_id = request.data.get('applicant_id')

        applicant = get_object_or_404(Applicant, applicant_id=applicant_id, eligibility_status='Eligible')

        verified_count = ApplicationDocument.objects.filter(applicant=applicant, verification_status='Verified').count()
        if verified_count == 0:
            return Response({"error": "All documents must be verified"}, status=status.HTTP_400_BAD_REQUEST)

        student_id = str(uuid.uuid4())[:10].upper()
        # Mock assign section
        section = Section.objects.filter(program=applicant.program_applied, available_seats__gt=0).first()
        if not section:
            return Response({"error": "No sections available"}, status=status.HTTP_400_BAD_REQUEST)

        admission = Admission.objects.create(
            student_id=student_id,
            applicant=applicant,
            program=applicant.program_applied,
            section=section,
            status='Active'
        )

        # Create fee record
        fee_view = CreateFeeRecord()
        fee_view.post(request._clone_with_data({'student_id': student_id}))

        applicant.status = 'Admitted'
        applicant.save()

        send_mail('Admission Confirmed', f'Congratulations! You are now enrolled with Student ID: {student_id}', 'no-reply@futurex.edu', [applicant.email], fail_silently=True)

        print(f"Admission finalized {student_id}")
        return Response({"message": f"Admission confirmed for applicant {applicant_id} → Student ID: {student_id}"}, status=status.HTTP_200_OK)

class CreateFeeRecord(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')

        admission = get_object_or_404(Admission, student_id=student_id)

        scholarship = Scholarship.objects.filter(applicant=admission.applicant, status='Approved').first()
        waiver = scholarship.waiver_percentage if scholarship else 0

        final_fee = round(admission.program.base_fee - (admission.program.base_fee * waiver / 100), 2)
        due_date = timezone.now().date() + timedelta(days=15)
        invoice_id = str(uuid.uuid4())[:10].upper()

        fee = StudentFee.objects.create(
            invoice_id=invoice_id,
            student=admission,
            total_amount=final_fee,
            due_date=due_date
        )

        send_mail('Fee Invoice Generated', f'Your fee invoice of Rs. {final_fee} is due by {due_date}', 'no-reply@futurex.edu', [admission.applicant.email], fail_silently=True)

        print(f"Fee record created {invoice_id}")
        return Response({"message": f"Fee record created for student {student_id} with payable amount Rs. {final_fee}"}, status=status.HTTP_200_OK)

class AssignSectionAndTimetable(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')

        admission = get_object_or_404(Admission, student_id=student_id)

        semester_no = 1  # Assume
        section = Section.objects.filter(
            program=admission.program,
            semester_no=semester_no,
            available_seats__gt=0
        ).order_by('available_seats').first()

        if not section:
            Waitlist.objects.create(student=admission, program=admission.program, semester_no=semester_no)
            return Response({"message": "No seats available — student added to waitlist"}, status=status.HTTP_200_OK)

        EnrollmentRecord.objects.create(
            student=admission,
            section=section,
            status='Active'
        )

        section.available_seats -= 1
        section.save()

        # Assign timetable (mock)
        Timetable.objects.get_or_create(section=section)

        print(f"Section assigned and timetable linked {student_id}")
        return Response({"message": f"Student assigned to section {section.section_name}"}, status=status.HTTP_200_OK)

class AdmissionReportGenerator(APIView):
    def post(self, request):
        period = request.data.get('period')  # e.g., '2025-01 to 2025-06'

        # Mock generating report
        start_date = timezone.now() - timedelta(days=30)
        end_date = timezone.now()

        admissions = Admission.objects.filter(admission_date__range=[start_date, end_date])

        if not admissions:
            return Response({"message": "No admission records found for selected period"}, status=status.HTTP_200_OK)

        # Mock data processing
        summary = [
            {"Program": "CS101", "Total Admissions": len(admissions), "Scholarships Awarded": 5}
        ]

        # Mock PDF generation
        report_path = f"/reports/admissions/{period.replace(' ', '_')}_admission_summary.pdf"

        print(f"Admission report generated for period {period}")
        return Response({"message": "Report generated", "path": report_path}, status=status.HTTP_200_OK)

# Model ViewSets for CRUD operations
class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [AllowAny]

class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [AllowAny]

class ApplicantViewSet(viewsets.ModelViewSet):
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    permission_classes = [AllowAny]

class ApplicationDocumentViewSet(viewsets.ModelViewSet):
    queryset = ApplicationDocument.objects.all()
    serializer_class = ApplicationDocumentSerializer
    permission_classes = [AllowAny]

class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.all()
    serializer_class = ScholarshipSerializer
    permission_classes = [AllowAny]

class InterviewScheduleViewSet(viewsets.ModelViewSet):
    queryset = InterviewSchedule.objects.all()
    serializer_class = InterviewScheduleSerializer
    permission_classes = [AllowAny]

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [AllowAny]

class AdmissionViewSet(viewsets.ModelViewSet):
    queryset = Admission.objects.all()
    serializer_class = AdmissionSerializer
    permission_classes = [AllowAny]

class StudentFeeViewSet(viewsets.ModelViewSet):
    queryset = StudentFee.objects.all()
    serializer_class = StudentFeeSerializer
    permission_classes = [AllowAny]

class EnrollmentRecordViewSet(viewsets.ModelViewSet):
    queryset = EnrollmentRecord.objects.all()
    serializer_class = EnrollmentRecordSerializer
    permission_classes = [AllowAny]

class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    permission_classes = [AllowAny]

class WaitlistViewSet(viewsets.ModelViewSet):
    queryset = Waitlist.objects.all()
    serializer_class = WaitlistSerializer
    permission_classes = [AllowAny]
