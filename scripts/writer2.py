import os

# Define the root directory of your project
root_dir = r'C:\Users\jcoul\Dev\ACTIVE\hvac-pro'

# --- 1. Refactored main.py with Landing Page Logic ---
# This update changes the root route ('/') to show the new landing page
# to logged-out users, while redirecting logged-in users to the dashboard.
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
    """
    Conditionally renders the landing page for logged-out users
    or redirects to the dashboard for logged-in users.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('landing_page.html')

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

# ... (The rest of your routes like /schedule, /api/schedule-job, etc. remain the same)
@main.route('/schedule')
@login_required
def schedule():
    scheduler = HVACScheduler()
    customers = scheduler.get_all_customers()
    technicians = scheduler.get_all_technicians()
    return render_template('schedule.html', customers=customers, technicians=technicians)

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
            flash(f"Job #{job.get('id')} scheduled successfully!", 'success')
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'No available slots found.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
'''

# --- 2. New File: templates/landing_page.html ---
# This is the brand new public-facing page for your application.
# It has its own simple structure and does not use the main app's base template.
landing_page_html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HVAC Pro - Run Your Business Smarter</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/landing.css') }}" rel="stylesheet">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-light fixed-top shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-bold" href="#">
                <i class="fas fa-tools text-primary"></i> HVAC Pro
            </a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('auth.login') }}">Login</a>
                    </li>
                    <li class="nav-item">
                        <a class="btn btn-primary" href="{{ url_for('auth.signup') }}">Get Started</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <header class="hero-section text-center text-white">
        <div class="container">
            <h1 class="display-3 fw-bold">Stop Juggling Spreadsheets.</h1>
            <p class="lead my-4">HVAC Pro centralizes your scheduling, customers, and invoicing, so you can focus on the work that matters.</p>
            <a class="btn btn-primary btn-lg" href="{{ url_for('auth.signup') }}">Start Running Your Business Smarter</a>
        </div>
    </header>

    <!-- Features Section -->
    <section class="features-section py-5">
        <div class="container">
            <div class="row text-center">
                <div class="col-md-4">
                    <div class="feature-item p-4">
                        <i class="fas fa-calendar-alt fa-3x text-primary mb-3"></i>
                        <h3 class="h5">Smart Scheduling</h3>
                        <p class="text-muted">Find the perfect time slot for any job based on technician availability and customer needs.</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="feature-item p-4">
                        <i class="fas fa-users fa-3x text-primary mb-3"></i>
                        <h3 class="h5">Customer Management</h3>
                        <p class="text-muted">Keep a complete history of every customer, from contact info to past jobs and preferences.</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="feature-item p-4">
                        <i class="fas fa-robot fa-3x text-primary mb-3"></i>
                        <h3 class="h5">Automated Follow-ups</h3>
                        <p class="text-muted">Boost customer loyalty with automatic maintenance reminders and satisfaction surveys.</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <footer class="text-center py-4 bg-light">
        <p class="mb-0">&copy; 2025 HVAC Pro. All Rights Reserved.</p>
    </footer>
</body>
</html>
'''

# --- 3. New File: static/css/landing.css ---
# This CSS file is dedicated to styling the new landing page.
landing_css_content = '''
body {
    padding-top: 56px; /* Offset for fixed navbar */
}
.hero-section {
    background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url('https://placehold.co/1920x1080/2c3e50/ffffff?text=HVAC+System');
    background-size: cover;
    background-position: center;
    padding: 8rem 0;
}
.feature-item i {
    transition: transform 0.2s ease-in-out;
}
.feature-item:hover i {
    transform: scale(1.2);
}
'''

# --- 4. Refactored templates/base.html with Sidebar Layout ---
# This is a complete rewrite of your base template to create the modern
# sidebar navigation layout for the logged-in application.
base_html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}HVAC Pro{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/custom.css') }}" rel="stylesheet">
</head>
<body>
    <div class="app-container">
        <!-- Sidebar Navigation -->
        <nav class="sidebar">
            <div class="sidebar-header">
                <a href="{{ url_for('main.dashboard') }}" class="sidebar-brand">
                    <i class="fas fa-tools"></i> HVAC Pro
                </a>
            </div>
            <ul class="sidebar-nav">
                <li class="sidebar-item {{ 'active' if 'dashboard' in request.endpoint else '' }}">
                    <a href="{{ url_for('main.dashboard') }}" class="sidebar-link">
                        <i class="fas fa-tachometer-alt"></i><span>Dashboard</span>
                    </a>
                </li>
                <li class="sidebar-item {{ 'schedule' in request.endpoint else '' }}">
                    <a href="{{ url_for('main.schedule') }}" class="sidebar-link">
                        <i class="fas fa-calendar-alt"></i><span>Schedule</span>
                    </a>
                </li>
                <!-- Add other links for Customers, Reports etc. here -->
            </ul>
        </nav>

        <!-- Main Content Area -->
        <main class="main-content">
            <header class="main-header">
                <button class="btn d-md-none" id="sidebar-toggle"><i class="fas fa-bars"></i></button>
                <div class="ms-auto d-flex align-items-center">
                    <div class="form-check form-switch me-3">
                        <input class="form-check-input" type="checkbox" id="darkModeToggle">
                        <label class="form-check-label" for="darkModeToggle"><i class="fas fa-moon"></i></label>
                    </div>
                    <a href="{{ url_for('auth.logout') }}" class="btn btn-outline-secondary">Logout</a>
                </div>
            </header>
            
            <div class="content-body">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                {% block content %}{% endblock %}
            </div>
        </main>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
'''

# --- 5. Updated static/css/custom.css with Sidebar and Dark Mode styles ---
# This is a major update to your CSS file to support the new layout.
custom_css_content = '''
/* Light Mode Variables (Default) */
:root {
    --bg-color: #f8f9fa;
    --text-color: #212529;
    --card-bg: #ffffff;
    --sidebar-bg: #2c3e50;
    --sidebar-text: #ecf0f1;
    --sidebar-link-hover: #34495e;
}

/* Dark Mode Variables */
.dark-mode {
    --bg-color: #121212;
    --text-color: #e0e0e0;
    --card-bg: #1e1e1e;
    --sidebar-bg: #1e1e1e;
    --sidebar-text: #e0e0e0;
    --sidebar-link-hover: #333333;
}

body {
    background-color: var(--bg-color);
    color: var(--text-color);
    transition: background-color 0.3s, color 0.3s;
}

.card {
    background-color: var(--card-bg);
    border: 1px solid rgba(0,0,0,0.1);
}
.dark-mode .card {
    border: 1px solid rgba(255,255,255,0.1);
}

/* App Layout */
.app-container {
    display: flex;
    min-height: 100vh;
}

/* Sidebar */
.sidebar {
    width: 250px;
    background-color: var(--sidebar-bg);
    color: var(--sidebar-text);
    transition: margin-left 0.3s;
}
.sidebar-header {
    padding: 1.25rem;
    text-align: center;
}
.sidebar-brand {
    color: var(--sidebar-text);
    text-decoration: none;
    font-size: 1.5rem;
    font-weight: bold;
}
.sidebar-nav {
    list-style: none;
    padding-left: 0;
}
.sidebar-link {
    display: block;
    padding: 1rem 1.5rem;
    color: var(--sidebar-text);
    text-decoration: none;
    transition: background-color 0.2s;
}
.sidebar-link i {
    margin-right: 1rem;
    width: 20px;
    text-align: center;
}
.sidebar-link:hover, .sidebar-item.active .sidebar-link {
    background-color: var(--sidebar-link-hover);
}

/* Main Content */
.main-content {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}
.main-header {
    padding: 1rem 1.5rem;
    background-color: var(--card-bg);
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    display: flex;
    align-items: center;
}
.content-body {
    padding: 1.5rem;
    flex-grow: 1;
}

/* Responsive (Mobile) Styles */
@media (max-width: 768px) {
    .sidebar {
        margin-left: -250px;
        position: fixed;
        height: 100%;
        z-index: 1000;
    }
    .sidebar.active {
        margin-left: 0;
    }
    .main-header {
        width: 100%;
    }
}
'''

# --- 6. New File: static/js/main.js ---
# This JavaScript file contains the logic for the dark mode toggle
# and the mobile hamburger menu.
main_js_content = '''
document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');

    // --- Dark Mode Logic ---
    // Check for saved dark mode preference
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
        darkModeToggle.checked = true;
    }

    darkModeToggle.addEventListener('change', () => {
        if (darkModeToggle.checked) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('darkMode', 'enabled');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('darkMode', 'disabled');
        }
    });

    // --- Sidebar Toggle Logic (for mobile) ---
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }
});
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
        'templates/landing_page.html': landing_page_html_content,
        'static/css/landing.css': landing_css_content,
        'templates/base.html': base_html_content,
        'static/css/custom.css': custom_css_content,
        'static/js/main.js': main_js_content
    }
    for file_path, content in files_to_update.items():
        full_path = os.path.join(root_dir, file_path)
        write_file(full_path, content)
    print("\n🎉 Modern UI/UX overhaul script finished successfully!")
    print("Restart your Flask server and visit http://127.0.0.1:5000 to see the new landing page.")
except Exception as e:
    print(f"❌ An error occurred: {e}")