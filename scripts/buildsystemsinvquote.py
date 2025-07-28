import os

# Define the root directory of your project
root_dir = r'C\Users\jcoul\Dev\ACTIVE\hvac-pro'

# --- 1. Update main.py to fix the scheduling bug ---
main_py_content = '''
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
'''

# --- 2. Update templates/schedule.html with client-side validation ---
schedule_html_content = '''
{% extends "base.html" %}
{% block title %}Schedule a Job{% endblock %}
{% block content %}
    {% endblock %}

{% block scripts %}
<script>
    document.getElementById('schedule-job-form').addEventListener('submit', async function(event) {
        event.preventDefault();

        const form = event.target;
        const customerId = document.getElementById('customer_id').value;

        // --- FIX: Add client-side validation ---
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
            alert('Error: ' + result.error);
        }
    });
</script>
{% endblock %}
'''

# --- 3. Update inventory.py blueprint with full functionality ---
inventory_py_content = '''
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.database import get_db_connection

inventory = Blueprint('inventory', __name__)

@inventory.route('/inventory')
@login_required
def list_parts():
    """Displays a list of all parts in inventory."""
    conn = get_db_connection()
    parts = conn.execute('SELECT * FROM parts ORDER BY name').fetchall()
    conn.close()
    return render_template('inventory/list.html', parts=parts)

@inventory.route('/inventory/add', methods=['GET', 'POST'])
@login_required
def add_part():
    """Handles adding a new part to inventory."""
    if request.method == 'POST':
        form_data = request.form
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO parts (name, sku, quantity_on_hand, cost_price, sale_price) VALUES (?, ?, ?, ?, ?)',
            (form_data['name'], form_data['sku'], form_data['quantity'], form_data['cost_price'], form_data['sale_price'])
        )
        conn.commit()
        conn.close()
        flash(f"Part '{form_data['name']}' added successfully!", 'success')
        return redirect(url_for('inventory.list_parts'))
    
    return render_template('inventory/form.html', part=None, title="Add New Part")
'''

# --- 4. New File: templates/inventory/list.html ---
inventory_list_html = '''
{% extends "base.html" %}
{% block title %}Inventory{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1 class="h2">Inventory Management</h1>
    <a href="{{ url_for('inventory.add_part') }}" class="btn btn-primary">
        <i class="fas fa-plus me-2"></i>Add New Part
    </a>
</div>
<div class="card shadow-sm">
    <div class="card-body">
        <table class="table table-striped table-hover">
            <thead class="table-light">
                <tr>
                    <th>Part Name</th>
                    <th>SKU</th>
                    <th>Quantity On Hand</th>
                    <th>Cost Price</th>
                    <th>Sale Price</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for part in parts %}
                <tr>
                    <td>{{ part.name }}</td>
                    <td>{{ part.sku or 'N/A' }}</td>
                    <td>
                        <span class="badge {{ 'bg-danger' if part.quantity_on_hand < 5 else 'bg-success' }}">
                            {{ part.quantity_on_hand }}
                        </span>
                    </td>
                    <td>${{ "%.2f"|format(part.cost_price or 0) }}</td>
                    <td>${{ "%.2f"|format(part.sale_price or 0) }}</td>
                    <td>
                        <a href="#" class="btn btn-sm btn-outline-secondary">Edit</a>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="6" class="text-center py-5">
                        <p class="text-muted">No parts in inventory yet.</p>
                        <a href="{{ url_for('inventory.add_part') }}" class="btn btn-primary">Add the first part</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
'''

# --- 5. New File: templates/inventory/form.html ---
inventory_form_html = '''
{% extends "base.html" %}
{% block title %}{{ title }}{% endblock %}
{% block content %}
<h1 class="h2 mb-4">{{ title }}</h1>
<div class="card shadow-sm">
    <div class="card-body">
        <form method="POST">
            <div class="row g-3">
                <div class="col-md-6">
                    <label for="name" class="form-label">Part Name</label>
                    <input type="text" class="form-control" id="name" name="name" value="{{ part.name or '' }}" required>
                </div>
                <div class="col-md-6">
                    <label for="sku" class="form-label">SKU (Part Number)</label>
                    <input type="text" class="form-control" id="sku" name="sku" value="{{ part.sku or '' }}">
                </div>
                <div class="col-md-4">
                    <label for="quantity" class="form-label">Quantity On Hand</label>
                    <input type="number" class="form-control" id="quantity" name="quantity" value="{{ part.quantity_on_hand or 0 }}" required>
                </div>
                <div class="col-md-4">
                    <label for="cost_price" class="form-label">Cost Price ($)</label>
                    <input type="number" step="0.01" class="form-control" id="cost_price" name="cost_price" value="{{ part.cost_price or '' }}">
                </div>
                <div class="col-md-4">
                    <label for="sale_price" class="form-label">Sale Price ($)</label>
                    <input type="number" step="0.01" class="form-control" id="sale_price" name="sale_price" value="{{ part.sale_price or '' }}">
                </div>
            </div>
            <hr class="my-4">
            <button type="submit" class="btn btn-primary">Save Part</button>
            <a href="{{ url_for('inventory.list_parts') }}" class="btn btn-secondary">Cancel</a>
        </form>
    </div>
</div>
{% endblock %}
'''

# --- 6. Update quotes.py with full functionality ---
quotes_py_content = '''
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.database import get_db_connection

quotes = Blueprint('quotes', __name__)

@quotes.route('/quotes')
@login_required
def list_quotes():
    conn = get_db_connection()
    all_quotes = conn.execute("""
        SELECT q.id, q.status, q.total_amount, q.created_at, c.name as customer_name
        FROM quotes q JOIN customers c ON q.customer_id = c.id
        ORDER BY q.created_at DESC
    """).fetchall()
    conn.close()
    return render_template('quotes/list.html', quotes=all_quotes)

@quotes.route('/quotes/new', methods=['GET', 'POST'])
@login_required
def create_quote():
    conn = get_db_connection()
    if request.method == 'POST':
        form_data = request.form
        
        # Create the main quote entry
        cursor = conn.cursor()
        cursor.execute('INSERT INTO quotes (customer_id, total_amount) VALUES (?, ?)',
                       (form_data['customer_id'], form_data['total_amount']))
        quote_id = cursor.lastrowid
        
        # Add line items
        descriptions = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        unit_prices = request.form.getlist('unit_price[]')
        
        for i in range(len(descriptions)):
            cursor.execute('INSERT INTO quote_line_items (quote_id, description, quantity, unit_price) VALUES (?, ?, ?, ?)',
                           (quote_id, descriptions[i], quantities[i], unit_prices[i]))
            
        conn.commit()
        conn.close()
        flash('Quote created successfully!', 'success')
        return redirect(url_for('quotes.list_quotes'))
    
    customers = conn.execute('SELECT id, name FROM customers ORDER BY name').fetchall()
    conn.close()
    return render_template('quotes/builder.html', customers=customers)
'''

# --- 7. New File: templates/quotes/list.html ---
quotes_list_html = '''
{% extends "base.html" %}
{% block title %}Quotes{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1 class="h2">Quote Management</h1>
    <a href="{{ url_for('quotes.create_quote') }}" class="btn btn-primary">
        <i class="fas fa-plus me-2"></i>Create New Quote
    </a>
</div>
<div class="card shadow-sm">
    <div class="card-body">
        <table class="table table-hover">
            <thead class="table-light">
                <tr>
                    <th>Quote #</th>
                    <th>Customer</th>
                    <th>Date</th>
                    <th>Total</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for quote in quotes %}
                <tr>
                    <td>{{ quote.id }}</td>
                    <td>{{ quote.customer_name }}</td>
                    <td>{{ quote.created_at[:10] }}</td>
                    <td>${{ "%.2f"|format(quote.total_amount or 0) }}</td>
                    <td>
                         <span class="badge bg-secondary">{{ quote.status | title }}</span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary">Convert to Job</button>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="6" class="text-center py-5">
                        <p class="text-muted">No quotes created yet.</p>
                        <a href="{{ url_for('quotes.create_quote') }}" class="btn btn-primary">Create the first quote</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
'''

# --- 8. New File: templates/quotes/builder.html ---
quote_builder_html = '''
{% extends "base.html" %}
{% block title %}Quote Builder{% endblock %}
{% block content %}
<h1 class="h2 mb-4">Quote Builder</h1>
<form method="POST">
    <div class="card shadow-sm mb-4">
        <div class="card-header">Customer Information</div>
        <div class="card-body">
            <label for="customer_id" class="form-label">Select Customer</label>
            <select class="form-select" id="customer_id" name="customer_id" required>
                <option disabled selected value="">Choose...</option>
                {% for customer in customers %}
                <option value="{{ customer.id }}">{{ customer.name }}</option>
                {% endfor %}
            </select>
        </div>
    </div>

    <div class="card shadow-sm">
        <div class="card-header">Line Items</div>
        <div class="card-body">
            <table class="table" id="line-items-table">
                <thead>
                    <tr>
                        <th>Description</th>
                        <th>Quantity</th>
                        <th>Unit Price</th>
                        <th>Total</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody id="line-items-body">
                    </tbody>
            </table>
            <button type="button" class="btn btn-secondary" onclick="addLineItem()">+ Add Line Item</button>
        </div>
        <div class="card-footer text-end">
            <input type="hidden" name="total_amount" id="total_amount_input">
            <h3 class="mb-0">Total: $<span id="total-amount">0.00</span></h3>
        </div>
    </div>
    <div class="mt-4">
        <button type="submit" class="btn btn-primary">Save Quote</button>
        <a href="{{ url_for('quotes.list_quotes') }}" class="btn btn-outline-secondary">Cancel</a>
    </div>
</form>
{% endblock %}

{% block scripts %}
<script>
    function addLineItem() {
        const tbody = document.getElementById('line-items-body');
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td><input type="text" name="description[]" class="form-control" required></td>
            <td><input type="number" name="quantity[]" class="form-control quantity" value="1" min="1" required></td>
            <td><input type="number" name="unit_price[]" class="form-control unit-price" step="0.01" min="0" required></td>
            <td class="line-total">$0.00</td>
            <td><button type="button" class="btn btn-danger btn-sm" onclick="this.closest('tr').remove(); calculateTotal();">X</button></td>
        `;
        tbody.appendChild(newRow);
    }

    function calculateTotal() {
        let total = 0;
        document.querySelectorAll('#line-items-body tr').forEach(row => {
            const quantity = parseFloat(row.querySelector('.quantity').value) || 0;
            const unitPrice = parseFloat(row.querySelector('.unit-price').value) || 0;
            const lineTotal = quantity * unitPrice;
            row.querySelector('.line-total').textContent = '$' + lineTotal.toFixed(2);
            total += lineTotal;
        });
        document.getElementById('total-amount').textContent = total.toFixed(2);
        document.getElementById('total_amount_input').value = total.toFixed(2);
    }

    document.getElementById('line-items-table').addEventListener('input', calculateTotal);
    
    // Add one line item to start
    addLineItem();
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
    # Update core files
    write_file(os.path.join(root_dir, 'main.py'), main_py_content)
    write_file(os.path.join(root_dir, 'templates/schedule.html'), schedule_html_content)
    write_file(os.path.join(root_dir, 'inventory.py'), inventory_py_content)
    write_file(os.path.join(root_dir, 'quotes.py'), quotes_py_content)
    
    # Create new template files
    os.makedirs(os.path.join(root_dir, 'templates/inventory'), exist_ok=True)
    os.makedirs(os.path.join(root_dir, 'templates/quotes'), exist_ok=True)
    write_file(os.path.join(root_dir, 'templates/inventory/list.html'), inventory_list_html)
    write_file(os.path.join(root_dir, 'templates/inventory/form.html'), inventory_form_html)
    write_file(os.path.join(root_dir, 'templates/quotes/list.html'), quotes_list_html)
    write_file(os.path.join(root_dir, 'templates/quotes/builder.html'), quote_builder_html)

    print("\n🎉 Core features (Inventory & Quotes) have been implemented!")
    print("Restart your Flask server and explore the new sections.")

except Exception as e:
    print(f"❌ An error occurred: {e}")