import os

# Define the root directory of your project
root_dir = r'C:\Users\jcoul\Dev\ACTIVE\hvac-pro'

# --- Corrected templates/base.html with proper Jinja2 syntax ---
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
                {# --- THIS IS THE CORRECTED SYNTAX --- #}
                <li class="sidebar-item {{ 'active' if 'dashboard' in request.endpoint else '' }}">
                    <a href="{{ url_for('main.dashboard') }}" class="sidebar-link">
                        <i class="fas fa-tachometer-alt"></i><span>Dashboard</span>
                    </a>
                </li>
                <li class="sidebar-item {{ 'active' if 'schedule' in request.endpoint else '' }}">
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

# --- Script to write the updated file ---
def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"✅ Updated file: {path}")

try:
    full_path = os.path.join(root_dir, 'templates/base.html')
    write_file(full_path, base_html_content)
    print("\n🎉 Corrected Jinja2 syntax in base.html.")
    print("Restart your Flask server to see the changes.")
except Exception as e:
    print(f"❌ An error occurred: {e}")