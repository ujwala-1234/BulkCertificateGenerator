from datetime import datetime
import uuid
from .extensions import db


class GenerationJob(db.Model):

    __tablename__ = "generation_jobs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    status = db.Column(
        db.String(30),
        default="pending",
        nullable=False
    )

    total = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    successful = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    failed = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    certificates = db.relationship(
        "Certificate",
        backref="job",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Certificate(db.Model):

    __tablename__ = "certificates"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("generation_jobs.id"),
        nullable=False
    )

    recipient_name = db.Column(
        db.String(150),
        nullable=False
    )

    recipient_email = db.Column(
        db.String(255),
        nullable=False
    )

    course = db.Column(
        db.String(200),
        nullable=False
    )

    # ADD THIS
    certificate_id = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    status = db.Column(
        db.String(30),
        default="pending",
        nullable=False
    )

    file_path = db.Column(
        db.String(500),
        nullable=True
    )

    error_message = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True
    )