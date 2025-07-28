
from flask import (
    Blueprint, render_template, redirect, url_for, request, jsonify, flash
)
from flask_login import login_required, current_user
from datetime import datetime
from models.scheduler import HVACScheduler
from services.data_analyzer import CustomerDataAnalyzer

main = Blueprint('main', __name__)

# ... (index, dashboard, schedule routes remain the same) ...

@main.route('/api/schedule-job', methods=['POST'])
@login_required
def schedule_job():
    data = request.json
    
    # --- FIX: Add server-side validation ---
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
