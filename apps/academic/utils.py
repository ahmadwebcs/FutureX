# academic/utils.py
from .models import Grade, Assessment
from django.db.models import Sum
import hashlib
import json
from django.template.loader import render_to_string
from weasyprint import HTML  # optional; you can use reportlab or wkhtmltopdf
import tempfile
import os

def compute_gpa_for_student(student):
    """
    Simple weighted average GPA calculation example.
    Returns (gpa, snapshot)
    snapshot is a dict of courses and grades used to compute GPA
    """
    qs = Grade.objects.filter(student=student).select_related('assessment__course', 'assessment')
    # group by course, compute weighted average
    per_course = {}
    for g in qs:
        course = g.assessment.course
        key = course.code
        per_course.setdefault(key, {'course_name': course.name, 'assessments': []})
        per_course[key]['assessments'].append({
            'assessment': g.assessment.name,
            'marks': g.marks_obtained,
            'max': g.assessment.max_marks,
            'weightage': g.assessment.weightage
        })

    # compute course percentages then average to a 'GPA' scale (custom)
    course_scores = []
    for key, val in per_course.items():
        total_weighted = 0.0
        total_weight = 0.0
        for a in val['assessments']:
            if a['max'] <= 0:
                continue
            pct = (a['marks'] / a['max']) * (a['weightage'])
            total_weighted += pct
            total_weight += a['weightage']
        if total_weight:
            normalized = (total_weighted / total_weight) * 100  # 0-100
            course_scores.append(normalized)

    if course_scores:
        # map 0-100 to 0.0-4.0 (simple mapping)
        avg_percent = sum(course_scores) / len(course_scores)
        gpa = round((avg_percent / 100) * 4.0, 2)
    else:
        gpa = 0.0

    snapshot = {'courses': per_course, 'computed_percent': avg_percent if course_scores else None}
    return gpa, snapshot

def generate_transcript_pdf(transcript):
    """
    Renders a simple transcript PDF using an HTML template and WeasyPrint.
    Returns path to saved file.
    """
    context = {
        'student': transcript.student,
        'gpa': transcript.gpa,
        'data': transcript.data,
        'created_at': transcript.created_at,
    }
    html_string = render_to_string('academic/transcript.html', context)
    html = HTML(string=html_string)
    tmpdir = tempfile.gettempdir()
    filename = os.path.join(tmpdir, f"transcript_{transcript.student.id}_{transcript.id}.pdf")
    html.write_pdf(target=filename)
    return filename

def blockchain_hash_for_data(data):
    """
    Simple SHA-256 hash of transcript data. In production you'd record to a blockchain or immutable ledger.
    """
    raw = json.dumps(data, sort_keys=True).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()
