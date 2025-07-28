import os

# Define the root directory of your project
root_dir = r'C:\Users\jcoul\Dev\ACTIVE\hvac-pro'

# --- 1. Updated main.py ---
# Ensures the schedule route provides all necessary data to the template.
main_py_content = '''
from flask import (
    Blueprint, render_template, redirect, url_for, request, jsonify, flash
)
from flask_login import login_required, current_user
from datetime import datetime
from models.scheduler import HVACScheduler
from services.data_analyzer import CustomerDataAnalyzer

main = Blueprint('main', __name__)

# ... (index, dashboard, and other routes remain the same) ...

@main.route('/schedule')
@login_required
def schedule():
    """Renders the scheduling page with necessary data for the form."""
    scheduler = HVACScheduler()
    customers = scheduler.get_all_customers()
    technicians = scheduler.get_all_technicians()
    return render_template('schedule.html', customers=customers, technicians=technicians)

# ... (rest of the routes and API endpoints) ...
'''

# --- 2. Overhauled templates/schedule.html ---
# This is a complete redesign of the scheduling page for a better UX.
schedule_html_content = '''
{% extends "base.html" %}
{% block title %}Schedule a Job{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1 class="h2">Schedule a New Job</h1>
</div>

<div class="row">
    <div class="col-lg-8 mx-auto">
        <div class="card shadow-sm">
            <div class="card-header">
                <h5 class="mb-0">Step 1: Job Details</h5>
            </div>
            <div class="card-body p-4">
                <form id="schedule-job-form">
                    <div class="row g-3">
                        <div class="col-12">
                            <label for="customer_id" class="form-label">Customer</label>
                            <select class="form-select" id="customer_id" name="customer_id" required>
                                <option value="" disabled selected>Select a customer...</option>
                                {% for customer in customers %}
                                    <option value="{{ customer.id }}">{{ customer.name }} - {{ customer.address }}</option>
                                {% endfor %}
                            </select>
                        </div>

                        <div class="col-md-6">
                            <label for="job_type" class="form-label">Job Type</label>
                            <select class="form-select" id="job_type" name="job_type" required>
                                <option value="maintenance">Maintenance</option>
                                <option value="repair">Repair</option>
                                <option value="installation">Installation</option>
                                <option value="electrical">Electrical</option>
                                <option value="quote">Quote/Estimate</option>
                            </select>
                        </div>

                        <div class="col-md-6">
                            <label for="priority" class="form-label">Priority</label>
                            <select class="form-select" id="priority" name="priority">
                                <option value="5">Low</option>
                                <option value="3" selected>Normal</option>
                                <option value="1">High (Emergency)</option>
                            </select>
                        </div>
                        
                        <div class="col-12">
                             <label for="preferred_date" class="form-label">Preferred Date (Optional)</label>
                             <input type="date" class="form-control" id="preferred_date" name="preferred_date">
                        </div>

                        <div class="col-12">
                            <label for="notes" class="form-label">Job Notes</label>
                            <textarea class="form-control" id="notes" name="notes" rows="4" placeholder="e.g., Customer reports rattling noise from outdoor AC unit. Check coolant levels. Access code for gate is #1234."></textarea>
                        </div>
                    </div>

                    <div class="d-grid gap-2 mt-4">
                        <button type="submit" class="btn btn-primary btn-lg">
                            <i class="fas fa-magic me-2"></i>Find Slot & Schedule
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    document.getElementById('schedule-job-form').addEventListener('submit', async function(event) {
        event.preventDefault();
        const form = event.target;
        const customerId = document.getElementById('customer_id').value;

        if (!customerId) {
            alert('Please select a customer before scheduling.');
            return;
        }

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        const response = await fetch("{{ url_for('main.schedule_job') }}", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (response.ok && result.success) {
            window.location.href = "{{ url_for('main.dashboard') }}";
        } else {
            alert('Error: ' + (result.error || 'An unknown error occurred.'));
        }
    });
</script>
{% endblock %}
'''

# --- Script to write the updated files ---
def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"✅ Wrote/Updated file: {path}")

try:
    files_to_update = {
        'main.py': main_py_content,
        'templates/schedule.html': schedule_html_content,
    }

    for file_path, content in files_to_update.items():
        full_path = os.path.join(root_dir, file_path)
        write_file(full_path, content)

    print("\n🎉 Schedule page has been fully implemented!")
    print("Restart your Flask server and refresh the Schedule page to see the changes.")

except Exception as e:
    print(f"❌ An error occurred: {e}")