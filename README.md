# Bulk Certificate Generator

## Objective

A Flask backend API that accepts multiple recipients in a single request and generates PDF certificates using a predefined certificate template.

The system creates one generation job for a bulk request, processes certificates individually, tracks progress, and allows generated certificates to be retrieved.

## Features

- Bulk certificate generation
- Input validation
- PDF certificate generation using ReportLab
- Background certificate processing
- Job status and progress tracking
- Individual certificate status tracking
- Individual certificate download
- Failure isolation — one failed certificate does not stop the remaining certificates
- Automated testing using Pytest

## Technology

- Python
- Flask
- MySQL
- SQLAlchemy
- ReportLab
- Pytest

## Project Structure

```text
BulkCertificateGenerator/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models.py
│   ├── routes.py
│   ├── services.py
│   └── certificate_generator.py
│
├── certificates/
│
├── tests/
│   ├── conftest.py
│   └── test_certificates.py
│
├── .env
├── .gitignore
├── pytest.ini
├── requirements.txt
├── run.py
└── README.md
```

## Database Setup

This project uses MySQL.

### 1. Start XAMPP

Start the MySQL service from XAMPP.

### 2. Create the database

Open phpMyAdmin or MySQL and run:

```sql
CREATE DATABASE certificate_generator;
```

The application creates the required database tables when initialized.

## Installation

### 1. Create a virtual environment

```bash
python -m venv venv
```

### 2. Activate the virtual environment

Windows PowerShell:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=bulk-certificate-secret

DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=root
DB_NAME=certificate_generator
DB_PORT=3307
```

Change the database credentials and port according to the local MySQL configuration.

## Run the Application

Start the Flask application:

```bash
python run.py
```

The application runs at:

```text
http://127.0.0.1:5000
```

## API Endpoints

### 1. Generate Bulk Certificates

**POST**

```text
/api/certificates/generate
```

Example:

```text
http://127.0.0.1:5000/api/certificates/generate
```

### Request

```json
{
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
```

### Successful Response

The API returns HTTP `202 Accepted` because certificate generation is processed as a background job.

Example:

```json
{
    "success": true,
    "job_id": 6
}
```

The returned job ID can be used to check the generation status.

## 2. Check Job Status

**GET**

```text
/api/certificates/jobs/<job_id>
```

Example:

```text
http://127.0.0.1:5000/api/certificates/jobs/6
```

Example response:

```json
{
    "success": true,
    "job": {
        "job_id": 6,
        "status": "completed",
        "total": 2,
        "successful": 2,
        "failed": 0,
        "pending": 0,
        "progress_percentage": 100.0,
        "certificates": [
            {
                "certificate_id": 4,
                "name": "Ujwala",
                "email": "ujwala@gmail.com",
                "course": "Python Full Stack",
                "status": "completed",
                "download_url": "/api/certificates/4/download"
            },
            {
                "certificate_id": 5,
                "name": "Rahul",
                "email": "rahul@gmail.com",
                "course": "Python Full Stack",
                "status": "completed",
                "download_url": "/api/certificates/5/download"
            }
        ]
    }
}
```

## 3. Download Certificate

**GET**

```text
/api/certificates/<certificate_id>/download
```

Example:

```text
http://127.0.0.1:5000/api/certificates/4/download
```

The API returns the generated PDF certificate.

Generated certificates are stored in:

```text
certificates/
```

## Certificate Template

A single predefined ReportLab template is used for certificate generation.

The certificate contains:

- Certificate title
- Recipient name
- Course name
- Recipient email
- Certificate ID

Each certificate is saved as an individual PDF file.

Example:

```text
certificates/
├── certificate_4.pdf
└── certificate_5.pdf
```

## Processing Design

The application creates one generation job for the complete recipient list.

The certificate generation process runs in a background thread so that the API can immediately accept the bulk request instead of waiting for every PDF to finish.

Processing flow:

```text
Client
   |
   | POST /api/certificates/generate
   v
Create Generation Job
   |
   v
Create Certificate Records
   |
   v
Background Processing
   |
   +---- Certificate 1
   |
   +---- Certificate 2
   |
   +---- Certificate N
   |
   v
Update Job Progress
   |
   v
Completed Job
```

## Failure Handling

Each certificate has an individual status:

```text
pending
processing
completed
failed
```

If certificate generation raises an exception, only that certificate is marked as `failed`.

The exception is handled inside the certificate-processing loop, allowing the remaining certificates to continue processing.

For example:

```text
Ujwala → failed
Rahul  → completed

Job status     → completed
Successful     → 1
Failed         → 1
```

This prevents one failed certificate from stopping the complete bulk generation job.

## Testing

Run the complete test suite:

```bash
pytest -v
```

The project currently contains six tests covering:

1. Creating a bulk generation job
2. Input validation
3. Certificate generation
4. Job status and progress
5. Certificate retrieval
6. Individual certificate failure handling

Current test result:

```text
6 passed
```

The individual failure test verifies that when one certificate fails, another valid certificate can still complete successfully.

## Design Decisions

### Background Processing

Certificate generation is performed in a background thread so the API can return quickly with a job ID.

### Relational Database

MySQL is used to persist generation jobs and certificate records.

### SQLAlchemy

SQLAlchemy provides database models and database access through Flask-SQLAlchemy.

### Individual Certificate Tracking

Each certificate maintains its own status, file path, and error message. This makes it possible to identify successful and failed certificates within the same bulk job.

### Failure Isolation

Certificate generation errors are handled individually. A failure in one certificate does not terminate the complete job.

## Example End-to-End Flow

```text
1. Client sends 2 recipients
        ↓
2. API creates Job ID
        ↓
3. API creates 2 certificate records
        ↓
4. Background processing starts
        ↓
5. PDF certificate for Ujwala is generated
        ↓
6. PDF certificate for Rahul is generated
        ↓
7. Job becomes completed
        ↓
8. Progress becomes 100%
        ↓
9. Client retrieves certificate information
        ↓
10. Client downloads individual PDF certificates
```

## Final Result

The Bulk Certificate Generator provides a complete backend workflow for generating multiple certificates from a single API request while supporting validation, progress tracking, individual failure handling, PDF generation, certificate retrieval, and automated testing.