import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
import time
import os
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
EMAIL_ADDRESS = os.getenv("ZOHO_EMAIL")
EMAIL_PASSWORD = os.getenv("ZOHO_PASSWORD")

SMTP_SERVER = "smtp.zoho.com"
SMTP_PORT = 587

if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise ValueError("Check your .env file! ZOHO_EMAIL or ZOHO_PASSWORD missing.")

# CSV of recipients
CSV_FILE = "influencers.csv"
LOG_FILE = "emails_sent.log"

# Read CSV
try:
    with open(CSV_FILE, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        recipients = list(reader)
except FileNotFoundError:
    print(f"{CSV_FILE} not found! Please create it locally.")
    recipients = []

# Load list of already emailed contacts to avoid duplicates
emailed = set()
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as f:
        emailed = set(line.strip() for line in f.readlines())

# Connect to Zoho SMTP
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

# Function to create the email content
def create_email(name, content_type):
    subject = f"Free 1-Year Access to Shareable Meals 🍽️"
    body = f"""Hi {name},

I love your {content_type} content! I’d like to offer you 1 year free access to my app, Shareable Meals, and a unique promo code for your audience. If you’re interested, just reply to this email and I’ll send you all the details!

Shareable Meals is a mobile app (iOS, currently in beta for Android) that makes meal planning simple and fun. With AI-powered meal creation, personalized nutrition tracking, and an easy-to-use calendar, it helps users plan, cook, and enjoy healthy meals. Normally, the app is $3.99/month, but I’d love to let you and your followers experience it free for a year.

Thanks for your time, and I hope you’ll check it out!

Best regards,
William Ashford
Founder, Shareable Meals
"""
    return subject, body

# Send emails
for r in recipients:
    email = r["email"]
    name = r["name"]
    content_type = r.get("content_type", "content")

    if email in emailed:
        print(f"Skipping {name} ({email}) — already emailed.")
        continue

    subject, body = create_email(name, content_type)

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server.send_message(msg)
        print(f"Email sent to {name} ({email})")
        # Log sent email
        with open(LOG_FILE, "a") as f:
            f.write(email + "\n")
        emailed.add(email)
        # Small delay to avoid spam filters
        time.sleep(10)
    except Exception as e:
        print(f"Failed to send email to {name} ({email}): {e}")

server.quit()
print("All emails processed.")
