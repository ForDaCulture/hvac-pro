import os

# Define the root directory of your project
root_dir = r'C:\Users\jcoul\Dev\ACTIVE\hvac-pro'

# --- Corrected main.py with the dashboard route restored ---
main_py_content = '''
from flask import (
    Blueprint, render_template, redirect, url_for, request, jsonify, flash
)
from flask_login import login_required, current_user
from datetime import datetime
from models.scheduler import HVACScheduler
from services.data_analyzer import CustomerDataAnalyzer

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('landing_page.html')

# --- THIS IS THE MISSING ROUTE ---
@main.route('/dashboard')
@login_required
def dashboard():
    """Displays the main dashboard with KPI cards and today's jobs."""
    scheduler = HVACScheduler()
    analyzer = CustomerDataAnalyzer()
    today_date = datetime.now().date()
    today_jobs = scheduler.get_jobs_by_date(today_date)
    
    kpi_stats = {
        'jobs_today': len(today_jobs),
        'revenue_this_week': scheduler.get_revenue_for_current_week(),
        'open_invoices': scheduler.get_open_invoice_count(),
        'at_risk_customers': len(analyzer.identify_at_risk_customers())
    }
    
    return render_template(
        'dashboard.html', 
        jobs=today_jobs, 
        kpi_stats=kpi_stats, 
        today=today_date
    )
# --- END MISSING ROUTE ---

@main.route('/schedule')
@login_required
def schedule():
    """Renders the scheduling page."""
    scheduler = HVACScheduler()
    customers = scheduler.get_all_customers()
    technicians = scheduler.get_all_technicians()
    return render_template('schedule.html', customers=customers, technicians=technicians)

@main.route('/api/schedule-job', methods=['POST'])
@login_required
def schedule_job():
    """API endpoint for scheduling a new job."""
    data = request.json
    if not data.get('customer_id'):
        return jsonify({'success': False, 'error': 'A customer must be selected.'}), 400

    scheduler = HVACScheduler()
    try:
        job = scheduler.auto_schedule_job(
            customer_id=data['customer_id'],
            job_type=data['job_type'],
            priority=data.get('priority', 3),
            preferred_date=data.get('preferred_date'),
            notes=data.get('notes', '')
        )
        if job:
            flash(f"Job #{job.get('id')} scheduled successfully!", 'success')
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'No available slots found.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
'''

# --- Script to write the updated file ---
def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"✅ Updated file: {path}")

try:
    full_path = os.path.join(root_dir, 'main.py')
    write_file(full_path, main_py_content)
    print("\n🎉 The 'dashboard' route has been restored in main.py.")
    print("Your server should restart automatically. Please refresh your browser.")

except Exception as e:
    print(f"❌ An error occurred: {e}")