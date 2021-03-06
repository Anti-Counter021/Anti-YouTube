from app.config import TESTS
from app.tasks import send_email as email


def send_email(
        email_to: str,
        subject_template: str = '',
        html_template: str = '',
        environment=None,
        attach: bool = False,
        file_name: str = '',
) -> None:
    if not TESTS:
        email.delay(email_to, subject_template, html_template, environment, attach, file_name)
