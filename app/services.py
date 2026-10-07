from datetime import datetime

from .extensions import db
from .models import GenerationJob, Certificate
from .certificate_generator import generate_certificate


def process_generation_job(app, job_id):

    with app.app_context():

        job = db.session.get(
            GenerationJob,
            job_id
        )

        if not job:
            return

        job.status = "processing"
        db.session.commit()

        certificates = Certificate.query.filter_by(
            job_id=job_id
        ).all()

        for certificate in certificates:

            if certificate.status == "failed":
                continue

            try:

                certificate.status = "processing"
                db.session.commit()

                file_path = generate_certificate(
                    name=certificate.recipient_name,
                    email=certificate.recipient_email,
                    course=certificate.course,
                    certificate_id=certificate.id,
                    output_folder=app.config[
                        "CERTIFICATE_FOLDER"
                    ]
                )

                certificate.status = "completed"
                certificate.file_path = file_path
                certificate.completed_at = datetime.utcnow()

                job.successful += 1

                db.session.commit()

            except Exception as error:

                certificate.status = "failed"
                certificate.error_message = str(error)
                certificate.completed_at = datetime.utcnow()

                job.failed += 1

                db.session.commit()

                # Continue processing the remaining certificates
                continue

        job.status = "completed"
        job.completed_at = datetime.utcnow()

        db.session.commit()