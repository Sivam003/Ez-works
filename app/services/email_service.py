from flask import current_app, render_template, url_for
from flask_mail import Message
from app import mail

def send_verification_email(user):
    """Send email verification to the user"""

    try:
        verification_url = url_for(
            'auth.verify_email',
            token=user.verification_token,
            _external=True
        )

        # Make sure subject and email are strings
        subject = "Verify your mail"
        recipient = str(user.email).strip()

        msg = Message(
            subject=subject,
            recipients=[recipient],
            html=render_template(
                'email/verification.html',
                user=user,
                verification_url=verification_url
            )
        )

        mail.send(msg)
        print("Email sent successfully to", recipient)
        return True

    except Exception as e:
        print("Error sending email:", e)
        return False
