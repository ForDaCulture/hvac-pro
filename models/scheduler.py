import sqlite3
from datetime import datetime, timedelta, time
import json
from .database import get_db_connection

class HVACScheduler:
    def __init__(self):
        self.business_hours = {
            'start': 8,      # 8 AM
            'end': 18,       # 6 PM
        }

    def get_jobs_by_date(self, date):
        """Get all jobs for a specific date."""
        conn = get_db_connection()
        # The rest of this method is the same...
        jobs = conn.execute("""
            SELECT j.*, c.name as customer_name, c.address, t.name as technician_name
            FROM jobs j
            JOIN customers c ON j.customer_id = c.id
            LEFT JOIN technicians t ON j.technician_id = t.id
            WHERE j.scheduled_date = ?
            ORDER BY j.scheduled_time
        """, (date,)).fetchall()
        conn.close()
        return [dict(row) for row in jobs]

    def get_all_customers(self):
        """Get all customers from the database."""
        conn = get_db_connection()
        customers = conn.execute('SELECT * FROM customers ORDER BY name').fetchall()
        conn.close()
        return [dict(row) for row in customers]

    def get_all_technicians(self):
        """Get all active technicians."""
        conn = get_db_connection()
        technicians = conn.execute('SELECT * FROM technicians WHERE active = 1 ORDER BY name').fetchall()
        conn.close()
        return [dict(row) for row in technicians]
        
    def auto_schedule_job(self, customer_id, job_type, priority, preferred_date, notes):
        """Logic to automatically schedule a job."""
        # For brevity, assuming the full scheduling logic is here
        print(f"Scheduling job for customer {customer_id}")
        return {'id': 99, 'status': 'scheduled'} # Example return
    
    # --- NEW METHODS ADDED HERE ---

    def get_revenue_for_current_week(self):
        """
        Calculates the total revenue from jobs completed in the current calendar week (Sun-Sat).
        """
        conn = get_db_connection()
        # This query finds the start of the week (last Sunday) and sums job_value
        result = conn.execute("""
            SELECT SUM(job_value) as weekly_revenue
            FROM jobs
            WHERE status = 'completed' AND completed_at >= date('now', 'weekday 0', '-6 days')
        """).fetchone()
        conn.close()
        return result['weekly_revenue'] if result and result['weekly_revenue'] else 0

    def get_open_invoice_count(self):
        """
        Gets a count of jobs completed in the last 30 days as a proxy for open invoices.
        """
        conn = get_db_connection()
        result = conn.execute("""
            SELECT COUNT(id) as invoice_count
            FROM jobs
            WHERE status = 'completed' AND completed_at >= date('now', '-30 days')
        """).fetchone()
        conn.close()
        return result['invoice_count'] if result and result['invoice_count'] else 0