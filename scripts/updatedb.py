import os

# Define the root directory of your project
root_dir = r'C:\Users\jcoul\Dev\ACTIVE\hvac-pro'

# --- The Complete and Correct models/database.py ---
# This version includes CREATE TABLE statements for ALL tables.
database_py_content = '''
import sqlite3
import os

DATABASE_PATH = 'hvac_business.db'

def get_db_connection():
    """Get database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """
    Initializes the database with all tables required for the application.
    This function is safe to run every time the app starts.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Create all tables IF THEY DON'T EXIST ---
    
    # User Authentication table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'technician', -- Roles: 'admin', 'technician'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(15),
            email VARCHAR(100),
            address TEXT,
            notes TEXT,
            preferred_time TEXT
        )
    """)
    
    # Technicians table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS technicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(15),
            email VARCHAR(100),
            skills TEXT,
            availability TEXT,
            hourly_rate REAL DEFAULT 35.00,
            active BOOLEAN DEFAULT 1
        )
    """)

    # Jobs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            technician_id INTEGER,
            job_type VARCHAR(50) NOT NULL,
            status VARCHAR(20) DEFAULT 'scheduled',
            scheduled_date DATE,
            scheduled_time TIME,
            notes TEXT,
            completed_at TIMESTAMP,
            job_value REAL,
            followup_sent BOOLEAN DEFAULT 0,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (technician_id) REFERENCES technicians (id)
        )
    """)

    # Parts Table (Inventory)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sku TEXT,
            quantity_on_hand INTEGER NOT NULL DEFAULT 0,
            cost_price REAL,
            sale_price REAL
        )
    """)

    # Quotes Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft',
            total_amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    """)

    # --- Insert Sample Data (only if customers table is empty) ---
    cursor.execute('SELECT COUNT(id) FROM customers')
    if cursor.fetchone()[0] == 0:
        insert_sample_data(cursor)

    conn.commit()
    conn.close()
    print("Database initialized and all tables verified.")

def insert_sample_data(cursor):
    """Inserts sample data for customers and technicians."""
    customers = [
        ('John Smith', '555-0101', 'john@example.com', '123 Main St, Nashua, NH', '["morning"]'),
        ('Sarah Johnson', '555-0102', 'sarah@example.com', '456 Oak Ave, Nashua, NH', '["afternoon"]')
    ]
    cursor.executemany("INSERT INTO customers (name, phone, email, address, preferred_time) VALUES (?, ?, ?, ?, ?)", customers)

    technicians = [
        ('Bob Martinez', '555-0201', 'bob@hvacpro.com', '["residential"]', '{}', 45.00),
        ('Lisa Chen', '555-0202', 'lisa@hvacpro.com', '["commercial"]', '{}', 40.00)
    ]
    cursor.executemany("INSERT INTO technicians (name, phone, email, skills, availability, hourly_rate) VALUES (?, ?, ?, ?, ?, ?)", technicians)
'''

# --- Script to write the updated file ---
def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"✅ Updated file: {path}")

try:
    full_path = os.path.join(root_dir, 'models/database.py')
    write_file(full_path, database_py_content)
    print("\n🎉 Corrected and completed the database initialization script.")
except Exception as e:
    print(f"❌ An error occurred: {e}")