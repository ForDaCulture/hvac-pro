
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
