import os

# Define the root directory of your project
root_dir = r'C:\Users\jcoul\Dev\ACTIVE\hvac-pro'

# --- 1. Updated inventory.py with full functionality ---
# This version adds the logic for viewing, adding, and editing parts.
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
            (form_data.get('name'), form_data.get('sku'), form_data.get('quantity'), form_data.get('cost_price'), form_data.get('sale_price'))
        )
        conn.commit()
        conn.close()
        flash(f"Part '{form_data.get('name')}' added successfully!", 'success')
        return redirect(url_for('inventory.list_parts'))
    
    return render_template('inventory/form.html', part=None, title="Add New Part", action_url=url_for('inventory.add_part'))

@inventory.route('/inventory/<int:part_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_part(part_id):
    """Handles editing an existing part."""
    conn = get_db_connection()
    if request.method == 'POST':
        form_data = request.form
        conn.execute(
            """UPDATE parts SET name = ?, sku = ?, quantity_on_hand = ?, cost_price = ?, sale_price = ?
               WHERE id = ?""",
            (form_data['name'], form_data['sku'], form_data['quantity'], form_data['cost_price'], form_data['sale_price'], part_id)
        )
        conn.commit()
        conn.close()
        flash(f"Part '{form_data['name']}' updated successfully!", 'success')
        return redirect(url_for('inventory.list_parts'))

    part = conn.execute('SELECT * FROM parts WHERE id = ?', (part_id,)).fetchone()
    conn.close()
    return render_template('inventory/form.html', part=part, title="Edit Part", action_url=url_for('inventory.edit_part', part_id=part_id))
'''

# --- 2. New File: templates/inventory/list.html ---
# This template creates the main table view for all your parts.
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
        <table class="table table-striped table-hover align-middle">
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
                        <span class="badge {{ 'bg-danger' if part.quantity_on_hand <= 5 else 'bg-success' }}">
                            {{ part.quantity_on_hand }}
                        </span>
                    </td>
                    <td>${{ "%.2f"|format(part.cost_price or 0) }}</td>
                    <td>${{ "%.2f"|format(part.sale_price or 0) }}</td>
                    <td>
                        <a href="{{ url_for('inventory.edit_part', part_id=part.id) }}" class="btn btn-sm btn-outline-secondary">
                            <i class="fas fa-edit"></i> Edit
                        </a>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="6" class="text-center py-5">
                        <i class="fas fa-box-open fa-3x text-muted mb-3"></i>
                        <h4 class="text-muted">No parts in inventory yet.</h4>
                        <a href="{{ url_for('inventory.add_part') }}" class="btn btn-primary mt-2">Add the first part</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
'''

# --- 3. New File: templates/inventory/form.html ---
# This template provides a reusable form for both adding and editing parts.
inventory_form_html = '''
{% extends "base.html" %}
{% block title %}{{ title }}{% endblock %}
{% block content %}
<h1 class="h2 mb-4">{{ title }}</h1>
<div class="card shadow-sm">
    <div class="card-body p-4">
        <form method="POST" action="{{ action_url }}">
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
                    <input type="number" class="form-control" id="quantity" name="quantity" value="{{ part.quantity_on_hand if part else 0 }}" required>
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

# --- Script to write the updated files ---
def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"✅ Wrote/Updated file: {path}")

try:
    files_to_update = {
        'inventory.py': inventory_py_content,
        'templates/inventory/list.html': inventory_list_html,
        'templates/inventory/form.html': inventory_form_html,
    }

    for file_path, content in files_to_update.items():
        full_path = os.path.join(root_dir, file_path)
        write_file(full_path, content)

    print("\n🎉 Inventory feature has been fully implemented!")
    print("Restart your Flask server and refresh the Inventory page to see the changes.")

except Exception as e:
    print(f"❌ An error occurred: {e}")