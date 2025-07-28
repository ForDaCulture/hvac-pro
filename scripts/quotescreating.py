import os

# Define the root directory of your project
root_dir = r'C:\Users\jcoul\Dev\ACTIVE\hvac-pro'

# --- 1. Updated quotes.py with full functionality ---
quotes_py_content = '''
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.database import get_db_connection

quotes = Blueprint('quotes', __name__)

@quotes.route('/quotes')
@login_required
def list_quotes():
    """Displays a list of all quotes, joining with customer names."""
    conn = get_db_connection()
    all_quotes = conn.execute("""
        SELECT q.id, q.status, q.total_amount, q.created_at, c.name as customer_name
        FROM quotes q 
        JOIN customers c ON q.customer_id = c.id
        ORDER BY q.created_at DESC
    """).fetchall()
    conn.close()
    return render_template('quotes/list.html', quotes=all_quotes)

@quotes.route('/quotes/new', methods=['GET', 'POST'])
@login_required
def create_quote():
    """Handles the creation of a new quote with its line items."""
    conn = get_db_connection()
    if request.method == 'POST':
        form_data = request.form
        
        cursor = conn.cursor()
        # Create the main quote entry
        cursor.execute('INSERT INTO quotes (customer_id, total_amount, status) VALUES (?, ?, ?)',
                       (form_data['customer_id'], form_data['total_amount'], 'draft'))
        quote_id = cursor.lastrowid
        
        # Add all line items from the form
        descriptions = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        unit_prices = request.form.getlist('unit_price[]')
        
        for i in range(len(descriptions)):
            if descriptions[i]: # Ensure description is not empty
                cursor.execute('INSERT INTO quote_line_items (quote_id, description, quantity, unit_price) VALUES (?, ?, ?, ?)',
                               (quote_id, descriptions[i], quantities[i], unit_prices[i]))
            
        conn.commit()
        conn.close()
        flash('Quote created successfully!', 'success')
        return redirect(url_for('quotes.list_quotes'))
    
    customers = conn.execute('SELECT id, name FROM customers ORDER BY name').fetchall()
    conn.close()
    return render_template('quotes/builder.html', customers=customers, quote=None, title="Create New Quote")

@quotes.route('/quotes/<int:quote_id>')
@login_required
def view_quote(quote_id):
    """Displays the details of a single quote."""
    conn = get_db_connection()
    quote = conn.execute("""
        SELECT q.*, c.name as customer_name, c.address as customer_address
        FROM quotes q JOIN customers c ON q.customer_id = c.id
        WHERE q.id = ?
    """, (quote_id,)).fetchone()
    
    line_items = conn.execute('SELECT * FROM quote_line_items WHERE quote_id = ?', (quote_id,)).fetchall()
    conn.close()
    
    return render_template('quotes/view.html', quote=quote, line_items=line_items)

@quotes.route('/quotes/<int:quote_id>/convert', methods=['POST'])
@login_required
def convert_to_job(quote_id):
    """Converts an approved quote into a new job in the scheduler."""
    conn = get_db_connection()
    quote = conn.execute('SELECT * FROM quotes WHERE id = ?', (quote_id,)).fetchone()
    
    # Create a new job based on the quote
    notes = f"Job created from approved Quote #{quote_id}."
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO jobs (customer_id, job_type, status, notes, job_value) VALUES (?, ?, ?, ?, ?)",
        (quote['customer_id'], 'Quoted Service', 'scheduled', notes, quote['total_amount'])
    )
    job_id = cursor.lastrowid
    
    # Update the quote status
    cursor.execute("UPDATE quotes SET status = 'approved' WHERE id = ?", (quote_id,))
    
    conn.commit()
    conn.close()
    
    flash(f'Quote #{quote_id} successfully converted to Job #{job_id}!', 'success')
    return redirect(url_for('main.dashboard'))
'''

# --- 2. New File: templates/quotes/list.html ---
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
        <table class="table table-hover align-middle">
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
                    <td>#{{ quote.id }}</td>
                    <td>{{ quote.customer_name }}</td>
                    <td>{{ quote.created_at[:10] }}</td>
                    <td>${{ "%.2f"|format(quote.total_amount or 0) }}</td>
                    <td>
                        {% set status_map = {
                            'draft': 'secondary',
                            'sent': 'info',
                            'approved': 'success',
                            'declined': 'danger'
                        } %}
                         <span class="badge bg-{{ status_map.get(quote.status, 'secondary') }}">{{ quote.status | title }}</span>
                    </td>
                    <td>
                        <a href="{{ url_for('quotes.view_quote', quote_id=quote.id) }}" class="btn btn-sm btn-outline-secondary">
                            View Details
                        </a>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="6" class="text-center py-5">
                        <i class="fas fa-file-invoice-dollar fa-3x text-muted mb-3"></i>
                        <h4 class="text-muted">No quotes created yet.</h4>
                        <a href="{{ url_for('quotes.create_quote') }}" class="btn btn-primary mt-2">Create the first quote</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
'''

# --- 3. New File: templates/quotes/builder.html ---
quote_builder_html = '''
{% extends "base.html" %}
{% block title %}{{ title }}{% endblock %}
{% block content %}
<h1 class="h2 mb-4">{{ title }}</h1>
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
                        <th style="width: 50%;">Description</th>
                        <th>Quantity</th>
                        <th>Unit Price</th>
                        <th>Total</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody id="line-items-body">
                    </tbody>
            </table>
            <button type="button" class="btn btn-outline-success" onclick="addLineItem()">+ Add Line Item</button>
        </div>
        <div class="card-footer text-end">
            <input type="hidden" name="total_amount" id="total_amount_input">
            <h3 class="mb-0">Total: $<span id="total-amount">0.00</span></h3>
        </div>
    </div>
    <div class="mt-4">
        <button type="submit" class="btn btn-primary btn-lg">Save Quote</button>
        <a href="{{ url_for('quotes.list_quotes') }}" class="btn btn-secondary">Cancel</a>
    </div>
</form>
{% endblock %}

{% block scripts %}
<script>
    function addLineItem() {
        const tbody = document.getElementById('line-items-body');
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td><input type="text" name="description[]" class="form-control" placeholder="Service or Part" required></td>
            <td><input type="number" name="quantity[]" class="form-control quantity" value="1" min="1" required></td>
            <td><input type="number" name="unit_price[]" class="form-control unit-price" placeholder="0.00" step="0.01" min="0" required></td>
            <td class="line-total fw-bold align-middle">$0.00</td>
            <td class="text-center"><button type="button" class="btn btn-danger btn-sm" onclick="this.closest('tr').remove(); calculateTotal();">&times;</button></td>
        `;
        tbody.appendChild(newRow);
    }

    function calculateTotal() {
        let grandTotal = 0;
        document.querySelectorAll('#line-items-body tr').forEach(row => {
            const quantity = parseFloat(row.querySelector('.quantity').value) || 0;
            const unitPrice = parseFloat(row.querySelector('.unit-price').value) || 0;
            const lineTotal = quantity * unitPrice;
            row.querySelector('.line-total').textContent = '$' + lineTotal.toFixed(2);
            grandTotal += lineTotal;
        });
        document.getElementById('total-amount').textContent = grandTotal.toFixed(2);
        document.getElementById('total_amount_input').value = grandTotal.toFixed(2);
    }

    // Add event listener to the table body for dynamic input changes
    document.getElementById('line-items-body').addEventListener('input', calculateTotal);
    
    // Add one line item to start
    addLineItem();
</script>
{% endblock %}
'''

# --- 4. New File: templates/quotes/view.html ---
quote_view_html = '''
{% extends "base.html" %}
{% block title %}Quote #{{ quote.id }}{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1 class="h2">Quote #{{ quote.id }} for {{ quote.customer_name }}</h1>
    <div>
        {% if quote.status == 'draft' or quote.status == 'sent' %}
        <form action="{{ url_for('quotes.convert_to_job', quote_id=quote.id) }}" method="POST" class="d-inline">
            <button type="submit" class="btn btn-success">
                <i class="fas fa-check me-2"></i>Convert to Job
            </button>
        </form>
        {% endif %}
    </div>
</div>

<div class="card shadow-sm">
    <div class="card-header">
        <strong>Status:</strong> <span class="badge bg-info">{{ quote.status | title }}</span>
        <strong class="ms-4">Date:</strong> {{ quote.created_at[:10] }}
    </div>
    <div class="card-body">
        <h5 class="card-title">Customer Details</h5>
        <p>{{ quote.customer_name }}<br>{{ quote.customer_address }}</p>
        <hr>
        <h5 class="card-title">Line Items</h5>
        <table class="table">
            <thead>
                <tr>
                    <th>Description</th>
                    <th class="text-end">Quantity</th>
                    <th class="text-end">Unit Price</th>
                    <th class="text-end">Total</th>
                </tr>
            </thead>
            <tbody>
                {% for item in line_items %}
                <tr>
                    <td>{{ item.description }}</td>
                    <td class="text-end">{{ item.quantity }}</td>
                    <td class="text-end">${{ "%.2f"|format(item.unit_price) }}</td>
                    <td class="text-end">${{ "%.2f"|format(item.quantity * item.unit_price) }}</td>
                </tr>
                {% endfor %}
            </tbody>
            <tfoot>
                <tr class="fw-bold">
                    <td colspan="3" class="text-end">Grand Total:</td>
                    <td class="text-end">${{ "%.2f"|format(quote.total_amount) }}</td>
                </tr>
            </tfoot>
        </table>
    </div>
</div>
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
        'quotes.py': quotes_py_content,
        'templates/quotes/list.html': quotes_list_html,
        'templates/quotes/builder.html': quote_builder_html,
        'templates/quotes/view.html': quote_view_html,
    }

    for file_path, content in files_to_update.items():
        full_path = os.path.join(root_dir, file_path)
        write_file(full_path, content)

    print("\n🎉 Quotes feature has been fully implemented!")
    print("Restart your Flask server and refresh the Quotes page to see the changes.")

except Exception as e:
    print(f"❌ An error occurred: {e}")