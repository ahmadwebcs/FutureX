# academic/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Grade, Attendance, Transcript, Program
from .tasks import notify_ai_tutor_grade, update_student_transcript, sync_program_with_university
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Grade)
def on_grade_saved(sender, instance, created, **kwargs):
    """
    Trigger AI-Tutor analysis and update transcripts asynchronously (task queued).
    """
    try:
        # enqueue Celery task (or call function if you don't use Celery)
        notify_ai_tutor_grade.delay(instance.id)
        update_student_transcript.delay(instance.student_id)
    except Exception as e:
        logger.exception("Failed to schedule tasks on grade save: %s", e)

@receiver(post_save, sender=Attendance)
def on_attendance_saved(sender, instance, created, **kwargs):
    # could trigger engagement analytics, for now we call AI-Tutor
    try:
        notify_ai_tutor_grade.delay(None)  # placeholder: consider different task for attendance
    except Exception as e:
        logger.exception("Failed to notify AI-Tutor on attendance save: %s", e)

# Example: schedule periodic sync when Program is updated locally
@receiver(post_save, sender=Program)
def on_program_saved(sender, instance, **kwargs):
    try:
        sync_program_with_university.delay(instance.id)
    except Exception as e:
        logger.exception("Failed queue program sync: %s", e)
