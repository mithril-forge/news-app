import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid


def send_email_with_proper_headers():
    SMTP_HOST = "localhost"
    SMTP_PORT = 587  # or 25
    SMTP_USER = "admin@localhost"
    SMTP_PASS = "admin123"
    TO_EMAIL = "noreply@localhost"

    # Create message with proper headers
    msg = MIMEText("Hello from my mail server!")
    msg['Subject'] = "Test Email"
    msg['From'] = SMTP_USER
    msg['To'] = TO_EMAIL
    msg['Date'] = formatdate(localtime=True)  # ← Add proper date
    msg['Message-ID'] = make_msgid()  # ← Add message ID

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        # Skip STARTTLS for now
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        print("✅ Email sent successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")


send_email_with_proper_headers()