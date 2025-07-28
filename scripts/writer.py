import os

# Define the root directory of your project
root_dir = r'C:\Users\jcoul\Dev\ACTIVE\hvac-pro'

# --- 1. Update main.py to flash a message on success ---
main_py_content = '''
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
'''

# --- 2. Update schedule.html to remove the alert and just redirect ---
schedule_html_content = '''
{% extends "base.html" %}
{% block title %}Schedule a Job - HVAC Pro{% endblock %}

{% block content %}
<div class="card shadow-lg mt-4">
    <div class="card-body p-5">
        <form id="schedule-job-form">
            <div class="d-grid gap-2 mt-4">
                <button type="submit" class="btn btn-primary btn-lg">
                    <i class="fas fa-magic"></i> Find Slot & Schedule
                </button>
            </div>
        </form>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    document.getElementById('schedule-job-form').addEventListener('submit', async function(event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        const response = await fetch("{{ url_for('main.schedule_job') }}", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        // --- THIS IS THE KEY CHANGE ---
        if (result.success) {
            // The alert is removed. We just redirect to the dashboard.
            // The flashed message from the server will be displayed there.
            window.location.href = "{{ url_for('main.dashboard') }}";
        } else {
            // Still show an alert for errors
            alert('Error: ' + result.error);
        }
    });
</script>
{% endblock %}
'''

# --- 3. Update base.html to display flashed messages ---
base_html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}HVAC Pro Dashboard{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/custom.css') }}" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
        </nav>

    <main class="container-fluid my-4">
        {# --- THIS IS THE NEWLY ADDED SECTION --- #}
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {# --- END NEW SECTION --- #}

        {% block content %}{% endblock %}
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
     {% block scripts %}{% endblock %}
</body>
</html>
'''

# --- Script to write the updated files ---
def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"✅ Updated file: {path}")

try:
    files_to_update = {
        'main.py': main_py_content,
        'templates/schedule.html': schedule_html_content,
        'templates/base.html': base_html_content
    }
    for file_path, content in files_to_update.items():
        full_path = os.path.join(root_dir, file_path)
        write_file(full_path, content)
    print("\n🎉 In-app notification system implemented successfully!")
    print("Restart your Flask server to see the changes.")
except Exception as e:
    print(f"❌ An error occurred: {e}")