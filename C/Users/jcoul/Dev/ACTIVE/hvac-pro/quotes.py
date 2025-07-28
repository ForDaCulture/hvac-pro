
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
