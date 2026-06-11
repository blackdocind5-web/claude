import argparse
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enviar reporte HTML por email")
    parser.add_argument("--file", required=True, help="Ruta al archivo HTML del reporte")
    args = parser.parse_args()

    report_path = Path(args.file)
    if not report_path.exists():
        print(f"Error: archivo no encontrado: {args.file}", file=sys.stderr)
        sys.exit(1)

    email_from = os.getenv("JARVIS_EMAIL_FROM", "").strip()
    email_password = os.getenv("JARVIS_EMAIL_PASSWORD", "").strip()
    email_to = os.getenv("JARVIS_EMAIL_TO", "").strip()
    smtp_host = os.getenv("JARVIS_EMAIL_SMTP", "smtp.gmail.com")
    smtp_port = int(os.getenv("JARVIS_EMAIL_PORT", "587"))

    if not all([email_from, email_password, email_to]):
        print(
            "Error: configurá JARVIS_EMAIL_FROM, JARVIS_EMAIL_PASSWORD y "
            "JARVIS_EMAIL_TO en tu archivo .env",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(report_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    subject = f"Jarvis — {report_path.stem}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = email_to
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(email_from, email_password)
            server.sendmail(email_from, email_to, msg.as_string())
        print(f"Email enviado a {email_to} — Asunto: {subject}")
    except Exception as e:
        print(f"Error al enviar email: {e}", file=sys.stderr)
        sys.exit(1)
