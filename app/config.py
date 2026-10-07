import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "bulk-certificate-secret"
    )

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://"
        f"{os.getenv('DB_USER', 'root')}:"
        f"{os.getenv('DB_PASSWORD', 'root')}@"
        f"{os.getenv('DB_HOST', '127.0.0.1')}:"
        f"{os.getenv('DB_PORT', '3307')}/"
        f"{os.getenv('DB_NAME', 'certificate_generator')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CERTIFICATE_FOLDER = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "certificates"
        )
    )

    BACKGROUND_PROCESSING = True