
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
