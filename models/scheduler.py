import sqlite3
from datetime import datetime, timedelta, time
import json
from models.database import get_db_connection

class HVACScheduler:
    def __init__(self):
        self.business_hours = {
            'start': 8,      # 8 AM
            'end': 18,       # 6 PM
            'lunch_start': 12, # 12 PM
            'lunch_end': 13    # 1 PM
        }
    
    def get_jobs_by_date(self, date):
        """Get all jobs for a specific date"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT j.*, c.name as customer_name, c.phone as customer_phone, 
                   c.address, t.name as technician_name
            FROM jobs j
            LEFT JOIN customers c ON j.customer_id = c.id
            LEFT JOIN technicians t ON j.technician_id = t.id
            WHERE j.scheduled_date = ?
            ORDER BY j.scheduled_time
        """, (date,))
        
        jobs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jobs
    
    def get_available_slots(self, date, duration_minutes=120):
        """Find available time slots for a given date"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT scheduled_time, estimated_duration, technician_id
            FROM jobs 
            WHERE scheduled_date = ? AND status != 'cancelled'
        """, (date,))
        scheduled_jobs = cursor.fetchall()
        
        cursor.execute('SELECT id FROM technicians WHERE active = 1')
        available_techs = [row['id'] for row in cursor.fetchall()]
        conn.close()
        
        available_slots = []
        start_minutes = self.business_hours['start'] * 60
        end_minutes = self.business_hours['end'] * 60
        
        # Check every 30-minute interval
        for time_slot in range(start_minutes, end_minutes - duration_minutes + 1, 30):
            # Skip lunch hour
            if (self.business_hours['lunch_start'] * 60 <= time_slot < 
                self.business_hours['lunch_end'] * 60):
                continue
            
            # Check if any technician is available
            for tech_id in available_techs:
                if self.is_technician_available(time_slot, duration_minutes, tech_id, scheduled_jobs):
                    slot_time = self.minutes_to_time(time_slot)
                    available_slots.append({
                        'time': slot_time,
                        'technician_id': tech_id
                    })
                    break  # Found one available tech, move to next slot
        
        return available_slots
    
    def is_technician_available(self, start_minutes, duration, tech_id, scheduled_jobs):
        """Check if a technician is available for a given time slot"""
        end_minutes = start_minutes + duration
        
        for job in scheduled_jobs:
            if job['technician_id'] != tech_id:
                continue
            
            job_time = datetime.strptime(job['scheduled_time'], '%H:%M:%S').time()
            job_start = job_time.hour * 60 + job_time.minute
            job_end = job_start + job['estimated_duration']
            
            # Check for overlap
            if start_minutes < job_end and end_minutes > job_start:
                return False
        
        return True
    
    def minutes_to_time(self, minutes):
        """Convert minutes since midnight to a time string"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
    
    def auto_schedule_job(self, customer_id, job_type, priority=3, preferred_date=None, notes=''):
        """Automatically find the best time slot and assign a technician"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT preferred_time FROM customers WHERE id = ?', (customer_id,))
        customer = cursor.fetchone()
        preferred_times = json.loads(customer['preferred_time'] if customer and customer['preferred_time'] else '[]')
        
        tech_skills_map = {
            'maintenance': ['residential', 'commercial'],
            'repair': ['residential', 'commercial'],
            'installation': ['residential', 'commercial'],
            'electrical': ['electrical']
        }
        required_skills = tech_skills_map.get(job_type, ['residential'])
        
        cursor.execute('SELECT id, skills FROM technicians WHERE active = 1')
        suitable_techs = []
        for tech in cursor.fetchall():
            tech_skills = json.loads(tech['skills'] if tech['skills'] else '[]')
            if any(skill in tech_skills for skill in required_skills):
                suitable_techs.append(tech['id'])
        
        if not suitable_techs:
            conn.close()
            return None
        
        duration_map = {
            'maintenance': 90, 'repair': 120,
            'installation': 180, 'electrical': 150
        }
        duration = duration_map.get(job_type, 120)
        
        search_dates = []
        if preferred_date:
            try:
                pref_date = datetime.strptime(preferred_date, '%Y-%m-%d').date()
                search_dates = [pref_date]
            except ValueError:
                pass
        
        if not search_dates:
            search_dates = [datetime.now().date() + timedelta(days=i) for i in range(7)]
        
        for target_date in search_dates:
            if target_date.weekday() >= 5: # Skip weekends
                continue
                
            available_slots = self.get_available_slots(target_date, duration)
            
            for slot in available_slots:
                slot_hour = int(slot['time'].split(':')[0])
                time_preference = self.get_time_preference(slot_hour)
                
                if not preferred_times or time_preference in preferred_times:
                    cursor.execute("""
                        INSERT INTO jobs (customer_id, technician_id, job_type, priority,
                                        scheduled_date, scheduled_time, estimated_duration, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (customer_id, slot['technician_id'], job_type, priority,
                          target_date, slot['time'], duration, notes))
                    
                    job_id = cursor.lastrowid
                    conn.commit()
                    
                    cursor.execute("""
                        SELECT j.*, c.name as customer_name, t.name as technician_name
                        FROM jobs j
                        LEFT JOIN customers c ON j.customer_id = c.id
                        LEFT JOIN technicians t ON j.technician_id = t.id
                        WHERE j.id = ?
                    """, (job_id,))
                    
                    job = dict(cursor.fetchone())
                    conn.close()
                    return job
        
        conn.close()
        return None  # No suitable slot found
    
    def get_time_preference(self, hour):
        """Convert an hour to a time preference string ('morning', 'afternoon', 'evening')"""
        if 6 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        else:
            return 'evening'
    
    def complete_job(self, job_id, completion_notes=''):
        """Mark a job as completed"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE jobs 
            SET status = 'completed', 
                completed_at = CURRENT_TIMESTAMP,
                notes = CASE 
                    WHEN notes IS NULL OR notes = '' THEN ?
                    ELSE notes || '

Completion: ' || ?
                END
            WHERE id = ?
        """, (completion_notes, completion_notes, job_id))
        
        conn.commit()
        conn.close()
    
    def get_all_customers(self):
        """Get all customers"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers ORDER BY name')
        customers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return customers
    
    def get_all_technicians(self):
        """Get all active technicians"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM technicians WHERE active = 1 ORDER BY name')
        technicians = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return technicians
    
    def add_customer(self, name, phone, email, address, notes=''):
        """Add a new customer"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO customers (name, phone, email, address, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (name, phone, email, address, notes))
        
        customer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return customer_id
    
    def get_job(self, job_id):
        """Get job details by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT j.*, c.name as customer_name, c.email as customer_email,
                   c.phone as customer_phone, c.address as customer_address,
                   t.name as technician_name
            FROM jobs j
            LEFT JOIN customers c ON j.customer_id = c.id
            LEFT JOIN technicians t ON j.technician_id = t.id
            WHERE j.id = ?
        """, (job_id,))
        
        job = cursor.fetchone()
        conn.close()
        return dict(job) if job else None
