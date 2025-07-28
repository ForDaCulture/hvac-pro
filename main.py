
from flask import (
    Blueprint, render_template, redirect, url_for, request, jsonify, flash
)
from flask_login import login_required
from datetime import datetime
from models.scheduler import HVACScheduler
from services.data_analyzer import CustomerDataAnalyzer

main = Blueprint('main', __name__)

# ... (other routes like index, dashboard, etc., remain the same) ...

@main.route('/')
@login_required
def index():
    return redirect(url_for('main.dashboard'))

@main.route('/dashboard')
@login_required
def dashboard():
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
    return render_template('dashboard.html', jobs=today_jobs, kpi_stats=kpi_stats, today=today_date)

@main.route('/schedule')
@login_required
def schedule():
    scheduler = HVACScheduler()
    customers = scheduler.get_all_customers()
    technicians = scheduler.get_all_technicians()
    return render_template('schedule.html', customers=customers, technicians=technicians)

# --- API Endpoints ---
@main.route('/api/schedule-job', methods=['POST'])
@login_required
def schedule_job():
    data = request.json
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
            # --- THIS IS THE KEY CHANGE ---
            # Flash a success message to be displayed on the next page
            flash(f"Job #{job.get('id')} scheduled successfully! View it on the dashboard.", 'success')
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'No available slots found.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
