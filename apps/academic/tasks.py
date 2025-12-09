# academic/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from .models import Grade, Transcript, Assessment, Course, Program
from django.contrib.auth import get_user_model
from django.db.models import Avg
from .utils import compute_gpa_for_student, generate_transcript_pdf, blockchain_hash_for_data
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task
def notify_ai_tutor_grade(grade_id):
    """
    Sends grade info to AI-Tutor microservice for analysis.
    AI_TUTOR_URL must be in settings as an env var.
    """
    payload = {}
    if grade_id:
        try:
            grade = Grade.objects.select_related('assessment__course', 'student').get(pk=grade_id)
            payload = {
                'student_id': grade.student.id,
                'assessment_id': grade.assessment.id,
                'course_id': grade.assessment.course.id,
                'marks': grade.marks_obtained,
                'max_marks': grade.assessment.max_marks,
            }
        except Grade.DoesNotExist:
            logger.warning("Grade %s not found", grade_id)
            return

    url = getattr(settings, 'AI_TUTOR_URL', None)
    if not url:
        logger.warning("AI_TUTOR_URL not configured")
        return

    try:
        r = requests.post(f"{url.rstrip('/')}/analyze/grade", json=payload, timeout=8)
        logger.info("AI-Tutor response: %s", r.status_code)
    except Exception as e:
        logger.exception("Failed to notify AI-Tutor: %s", e)

@shared_task
def update_student_transcript(student_id):
    """
    Recalculate transcript (GPA) for a student and create/update Transcript model.
    """
    try:
        student = User.objects.get(pk=student_id)
    except User.DoesNotExist:
        logger.warning("Student not found: %s", student_id)
        return

    # compute gpa with helper util
    gpa, snapshot = compute_gpa_for_student(student)

    t, _ = Transcript.objects.update_or_create(
        student=student,
        defaults={'gpa': gpa, 'data': snapshot}
    )

    # Optionally generate signed pdf and blockchain hash
    try:
        pdf_path = generate_transcript_pdf(t)  # returns path or bytes
        block_hash = blockchain_hash_for_data(t.data)
        t.blockchain_hash = block_hash
        t.save()
    except Exception as e:
        logger.exception("Failed to generate transcript PDF or blockchain hash: %s", e)

@shared_task
def sync_program_with_university(program_id):
    """
    Example: fetch updated syllabus from central Uni API and update local Program and Courses.
    UNIVERSITY_API_URL should be in settings.
    """
    from .models import Program, Course
    url = getattr(settings, 'UNIVERSITY_API_URL', None)
    if not url:
        logger.warning("UNIVERSITY_API_URL not configured")
        return
    try:
        program = Program.objects.get(pk=program_id)
    except Program.DoesNotExist:
        logger.warning("Program not found: %s", program_id)
        return

    try:
        r = requests.get(f"{url.rstrip('/')}/programs/{program.code}", timeout=10)
        if r.status_code != 200:
            logger.warning("University API returned %s", r.status_code)
            return
        payload = r.json()
        # example mapping; adapt to real API
        program.name = payload.get('name', program.name)
        program.total_credits = payload.get('total_credits', program.total_credits)
        program.last_synced = None
        program.save()
        # update courses
        for c in payload.get('courses', []):
            Course.objects.update_or_create(
                code=c['code'],
                defaults={
                    'name': c['name'],
                    'credit_hours': c.get('credit_hours', 0),
                    'program': program
                }
            )
    except Exception as e:
        logger.exception("Failed to sync program: %s", e)
