from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from models.database import get_db_connection
import atexit

class FollowUpAutomation:
    def __init__(self):
        self.twilio_client = self._init_twilio()
        self.sg_client = self._init_sendgrid()
        self.scheduler = BackgroundScheduler(daemon=True)
        atexit.register(lambda: self.scheduler.shutdown())

    def _init_twilio(self):
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        if account_sid and auth_token:
            return Client(account_sid, auth_token)
        print("Twilio credentials not found.")
        return None

    def _init_sendgrid(self):
        api_key = os.environ.get('SENDGRID_API_KEY')
        if api_key:
            return SendGridAPIClient(api_key)
        print("SendGrid API key not found.")
        return None

    def start(self):
        """Schedule and start all follow-up tasks."""
        self.scheduler.add_job(self.daily_followup_check, 'cron', hour=9, minute=30, id='daily_followup_check')
        self.scheduler.add_job(self.weekly_maintenance_reminders, 'cron', day_of_week='mon', hour=10, id='maintenance_reminders')
        self.scheduler.start()
        print("✅ Follow-up automation scheduler started.")

    def daily_followup_check(self):
        """Send a satisfaction survey for jobs completed yesterday."""
        print("Running daily followup check...")
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        conn = get_db_connection()
        try:
            jobs = conn.execute("""
                SELECT j.id, j.job_type, c.name, c.email, c.phone FROM jobs j
                JOIN customers c ON j.customer_id = c.id
                WHERE DATE(j.completed_at) = ? AND j.status = 'completed' AND j.followup_sent = 0
            """, (yesterday,)).fetchall()

            for job in jobs:
                print(f"Sending survey for job {job['id']} to {job['name']}")
                self._send_satisfaction_survey(dict(job))
                conn.execute("UPDATE jobs SET followup_sent = 1 WHERE id = ?", (job['id'],))
            conn.commit()
        finally:
            conn.close()
            
    def _send_satisfaction_survey(self, job):
        """Sends a survey via SMS or email."""
        message_body = f"Hi {job['name']}, thank you for choosing us for your recent {job['job_type']} service. We'd love your feedback! - {os.environ.get('BUSINESS_NAME')}"
        # Prioritize SMS
        if self.twilio_client and job['phone']:
            try:
                self.twilio_client.messages.create(
                    body=message_body,
                    from_=os.environ.get('TWILIO_PHONE_NUMBER'),
                    to=job['phone']
                )
                return True
            except Exception as e:
                print(f"Twilio SMS failed: {e}")
        # Fallback to email
        if self.sg_client and job['email']:
            return self._send_email(job['email'], "Your Feedback is Important to Us", message_body)
        return False
        
    def weekly_maintenance_reminders(self):
        """Send maintenance reminders to customers due for service."""
        print("Running weekly maintenance reminders...")
        six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        conn = get_db_connection()
        try:
            customers = conn.execute("""
                SELECT c.name, c.email, c.phone FROM customers c WHERE c.id NOT IN (
                    SELECT DISTINCT j.customer_id FROM jobs j WHERE j.job_type = 'maintenance' AND j.completed_at > ?
                )
            """, (six_months_ago,)).fetchall()

            for customer in customers:
                 self._send_maintenance_reminder(dict(customer))
        finally:
            conn.close()

    def _send_maintenance_reminder(self, customer):
        message_body = f"Hi {customer['name']}, it's time for your seasonal HVAC maintenance. Regular check-ups prevent costly repairs! Call us to schedule. - {os.environ.get('BUSINESS_NAME')}"
        if self.sg_client and customer['email']:
            self._send_email(customer['email'], "Time for your HVAC Maintenance!", message_body)

    def _send_email(self, to_email, subject, body):
        """Helper function to send email via SendGrid."""
        try:
            message = Mail(
                from_email=os.environ.get('BUSINESS_EMAIL'),
                to_emails=to_email,
                subject=subject,
                html_content=f'<strong>{body}</strong>'
            )
            self.sg_client.send(message)
            return True
        except Exception as e:
            print(f"SendGrid email failed: {e}")
            return False

# This block allows the script to be run as a standalone worker process
if __name__ == "__main__":
    automation = FollowUpAutomation()
    automation.start()
    
    # Keep the script running
    import time
    try:
        while True:
            time.sleep(3600) # Sleep for an hour
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down followup scheduler.")
