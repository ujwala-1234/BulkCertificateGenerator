import pytest

from app import create_app
from app.extensions import db
from app.models import Certificate,GenerationJob


@pytest.fixture
def app(tmp_path):

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": (
            "sqlite:///"
            + str(tmp_path / "test.db")
        ),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "CERTIFICATE_FOLDER": str(
            tmp_path / "certificates"
        ),
        "BACKGROUND_PROCESSING": False
    })

    with app.app_context():
        db.drop_all()
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# 1. Test creating a bulk generation job
def test_create_generation_job(client):

    response = client.post(
        "/api/certificates/generate",
        json={
            "recipients": [
                {
                    "name": "Ujwala",
                    "email": "ujwala@gmail.com",
                    "course": "Python Full Stack"
                },
                {
                    "name": "Rahul",
                    "email": "rahul@gmail.com",
                    "course": "Python Full Stack"
                }
            ]
        }
    )

    # POST endpoint returns 202 Accepted
    assert response.status_code == 202

    data = response.get_json()

    assert data["success"] is True
    assert "job_id" in data


# 2. Test input validation
def test_input_validation(client):

    response = client.post(
        "/api/certificates/generate",
        json={
            "recipients": []
        }
    )

    assert response.status_code == 400


# 3. Test certificate generation records
def test_certificate_generation(client, app):

    response = client.post(
        "/api/certificates/generate",
        json={
            "recipients": [
                {
                    "name": "Ujwala",
                    "email": "ujwala@gmail.com",
                    "course": "Python Full Stack"
                }
            ]
        }
    )

    # POST endpoint returns 202 Accepted
    assert response.status_code == 202

    data = response.get_json()
    job_id = data["job_id"]

    with app.app_context():

        certificates = Certificate.query.filter_by(
            job_id=job_id
        ).all()

        assert len(certificates) == 1
        assert certificates[0].recipient_name == "Ujwala"
        assert certificates[0].course == "Python Full Stack"


# 4. Test job status and progress
def test_job_status_progress(client):

    response = client.post(
        "/api/certificates/generate",
        json={
            "recipients": [
                {
                    "name": "Ujwala",
                    "email": "ujwala@gmail.com",
                    "course": "Python Full Stack"
                },
                {
                    "name": "Rahul",
                    "email": "rahul@gmail.com",
                    "course": "Python Full Stack"
                }
            ]
        }
    )

    assert response.status_code == 202

    data = response.get_json()
    job_id = data["job_id"]

    response = client.get(
        f"/api/certificates/jobs/{job_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["job"]["job_id"] == job_id
    assert data["job"]["total"] == 2


# 5. Test retrieving generated certificates
def test_retrieve_certificates(client):

    response = client.post(
        "/api/certificates/generate",
        json={
            "recipients": [
                {
                    "name": "Ujwala",
                    "email": "ujwala@gmail.com",
                    "course": "Python Full Stack"
                }
            ]
        }
    )

    assert response.status_code == 202

    data = response.get_json()
    job_id = data["job_id"]

    response = client.get(
        f"/api/certificates/jobs/{job_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    certificates = data["job"]["certificates"]

    assert len(certificates) == 1
    assert certificates[0]["name"] == "Ujwala"
    assert certificates[0]["status"] == "completed"
# 6. Test individual certificate failure
def test_individual_certificate_failure(client, app, monkeypatch):

    from app import services

    def fake_generate_certificate(*args, **kwargs):

        if kwargs["name"] == "Ujwala":
            raise Exception("Test certificate generation failure")

        certificate_id = kwargs["certificate_id"]
        output_folder = kwargs["output_folder"]

        return f"{output_folder}/certificate_{certificate_id}.pdf"

    monkeypatch.setattr(
        services,
        "generate_certificate",
        fake_generate_certificate
    )

    response = client.post(
        "/api/certificates/generate",
        json={
            "recipients": [
                {
                    "name": "Ujwala",
                    "email": "ujwala@gmail.com",
                    "course": "Python Full Stack"
                },
                {
                    "name": "Rahul",
                    "email": "rahul@gmail.com",
                    "course": "Python Full Stack"
                }
            ]
        }
    )

    assert response.status_code == 202

    data = response.get_json()
    job_id = data["job_id"]

    with app.app_context():

        job = db.session.get(
            GenerationJob,
            job_id
        )

        certificates = Certificate.query.filter_by(
            job_id=job_id
        ).all()

        ujwala = next(
            c for c in certificates
            if c.recipient_name == "Ujwala"
        )

        rahul = next(
            c for c in certificates
            if c.recipient_name == "Rahul"
        )

        assert ujwala.status == "failed"
        assert rahul.status == "completed"

        assert job.failed == 1
        assert job.successful == 1
        assert job.status == "completed"
