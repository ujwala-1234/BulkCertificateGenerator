import re
import threading

from flask import (
    Blueprint,
    jsonify,
    request,
    send_file,
    current_app
)

from .extensions import db
from .models import GenerationJob, Certificate
from .services import process_generation_job


certificate_bp = Blueprint(
    "certificates",
    __name__,
    url_prefix="/api/certificates"
)


EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


def validate_recipient(recipient):

    errors = []

    if not isinstance(recipient, dict):
        return ["Recipient must be an object"]

    name = recipient.get("name")
    email = recipient.get("email")
    course = recipient.get("course")

    if not isinstance(name, str) or not name.strip():
        errors.append("name is required")

    if not isinstance(email, str) or not EMAIL_PATTERN.match(email):
        errors.append("valid email is required")

    if not isinstance(course, str) or not course.strip():
        errors.append("course is required")

    return errors


@certificate_bp.route(
    "/generate",
    methods=["POST"]
)
def generate_certificates():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):

        return jsonify({
            "success": False,
            "message": "Request body must be JSON"
        }), 400

    recipients = data.get("recipients")

    if not isinstance(recipients, list):

        return jsonify({
            "success": False,
            "message": "recipients must be a list"
        }), 400

    if len(recipients) == 0:

        return jsonify({
            "success": False,
            "message": "At least one recipient is required"
        }), 400

    if len(recipients) > 500:

        return jsonify({
            "success": False,
            "message": "Maximum 500 recipients are allowed"
        }), 400

    job = GenerationJob(
        status="pending",
        total=len(recipients)
    )

    db.session.add(job)
    db.session.flush()

    for recipient in recipients:

        errors = validate_recipient(recipient)

        if errors:

            certificate = Certificate(
                job_id=job.id,
                recipient_name=recipient.get(
                    "name",
                    "Unknown"
                ),
                recipient_email=recipient.get(
                    "email",
                    ""
                ),
                course=recipient.get(
                    "course",
                    "Unknown"
                ),
                status="failed",
                error_message="; ".join(errors)
            )

            job.failed += 1

        else:

            certificate = Certificate(
                job_id=job.id,
                recipient_name=recipient["name"].strip(),
                recipient_email=recipient["email"].strip(),
                course=recipient["course"].strip(),
                status="pending"
            )

        db.session.add(certificate)

    db.session.commit()

    app = current_app._get_current_object()

    if app.config["BACKGROUND_PROCESSING"]:

        thread = threading.Thread(
            target=process_generation_job,
            args=(app, job.id),
            daemon=True
        )

        thread.start()

    else:

        process_generation_job(
            app,
            job.id
        )

    return jsonify({
        "success": True,
        "message": "Certificate generation job created",
        "job_id": job.id,
        "status_url": f"/api/certificates/jobs/{job.id}"
    }), 202


@certificate_bp.route(
    "/jobs/<int:job_id>",
    methods=["GET"]
)
def get_job_status(job_id):

    job = db.session.get(
        GenerationJob,
        job_id
    )

    if not job:

        return jsonify({
            "success": False,
            "message": "Job not found"
        }), 404

    certificates = Certificate.query.filter_by(
        job_id=job.id
    ).all()

    results = []

    for certificate in certificates:

        result = {
            "certificate_id": certificate.id,
            "name": certificate.recipient_name,
            "email": certificate.recipient_email,
            "course": certificate.course,
            "status": certificate.status
        }

        if certificate.status == "completed":

            result["download_url"] = (
                f"/api/certificates/"
                f"{certificate.id}/download"
            )

        if certificate.status == "failed":

            result["error"] = certificate.error_message

        results.append(result)

    return jsonify({
        "success": True,
        "job": {
            "job_id": job.id,
            "status": job.status,
            "total": job.total,
            "successful": job.successful,
            "failed": job.failed,
            "pending": (
                job.total
                - job.successful
                - job.failed
            ),
            "progress_percentage": (
                round(
                    (
                        (job.successful + job.failed)
                        / job.total
                    ) * 100,
                    2
                )
                if job.total
                else 100
            ),
            "certificates": results
        }
    })


@certificate_bp.route(
    "/<int:certificate_id>/download",
    methods=["GET"]
)
def download_certificate(certificate_id):

    certificate = db.session.get(
        Certificate,
        certificate_id
    )

    if not certificate:

        return jsonify({
            "success": False,
            "message": "Certificate not found"
        }), 404

    if certificate.status != "completed":

        return jsonify({
            "success": False,
            "message": "Certificate is not available"
        }), 404

    return send_file(
        certificate.file_path,
        as_attachment=True,
        download_name=(
            f"{certificate.recipient_name}"
            f"_certificate.pdf"
        ),
        mimetype="application/pdf"
    )