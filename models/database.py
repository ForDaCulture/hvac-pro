import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'hvac_business.db'

def get_db_connection():
    """Get database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the SQLite database with required tables and sample data."""
    if os.path.exists(DATABASE_PATH):
        # Avoid re-initializing if the DB already exists.
        # For a real app, you'd use a migration tool like Alembic.
        return
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(15),
                email VARCHAR(100),
                address TEXT,
                notes TEXT,
                preferred_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create technicians table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS technicians (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(15),
                email VARCHAR(100),
                skills TEXT,
                availability TEXT,
                hourly_rate DECIMAL(10,2) DEFAULT 35.00,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                technician_id INTEGER,
                job_type VARCHAR(50) NOT NULL,
                priority INTEGER DEFAULT 3,
                scheduled_date DATE,
                scheduled_time TIME,
                estimated_duration INTEGER DEFAULT 120,
                actual_duration INTEGER,
                status VARCHAR(20) DEFAULT 'scheduled',
                notes TEXT,
                parts_needed TEXT,
                job_value DECIMAL(10,2),
                followup_sent BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (technician_id) REFERENCES technicians (id)
            )
        """)

        # Create parts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                part_number VARCHAR(50),
                category VARCHAR(50),
                unit_cost DECIMAL(10,2),
                quantity_in_stock INTEGER DEFAULT 0,
                reorder_level INTEGER DEFAULT 5,
                supplier VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create job_parts table (many-to-many relationship)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                part_id INTEGER NOT NULL,
                quantity_used INTEGER NOT NULL,
                cost_per_unit DECIMAL(10,2),
                FOREIGN KEY (job_id) REFERENCES jobs (id),
                FOREIGN KEY (part_id) REFERENCES parts (id)
            )
        """)

        # Insert sample data since the database is being created
        insert_sample_data(cursor)

        # Commit changes
        conn.commit()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def insert_sample_data(cursor):
    """Insert sample data into the database for testing purposes."""
    try:
        # Sample customers
        customers = [
            ('John Smith', '555-0101', 'john@email.com', '123 Main St, Anytown, ST 12345', '["morning"]'),
            ('Sarah Johnson', '555-0102', 'sarah@email.com', '456 Oak Ave, Anytown, ST 12345', '["afternoon"]'),
            ('Mike Wilson', '555-0103', 'mike@email.com', '789 Pine Rd, Anytown, ST 12345', '["evening"]')
        ]
        cursor.executemany("""
            INSERT INTO customers (name, phone, email, address, preferred_time)
            VALUES (?, ?, ?, ?, ?)
        """, customers)

        # Sample technicians
        technicians = [
            ('Bob Martinez', '555-0201', 'bob@hvacpro.com', '["residential", "commercial"]', '{"monday": "8-17", "tuesday": "8-17", "wednesday": "8-17", "thursday": "8-17", "friday": "8-17"}', 45.00),
            ('Lisa Chen', '555-0202', 'lisa@hvacpro.com', '["residential", "electrical"]', '{"monday": "9-18", "tuesday": "9-18", "wednesday": "9-18", "thursday": "9-18", "friday": "9-18"}', 40.00)
        ]
        cursor.executemany("""
            INSERT INTO technicians (name, phone, email, skills, availability, hourly_rate)
            VALUES (?, ?, ?, ?, ?, ?)
        """, technicians)

        # Sample parts
        parts = [
            ('Air Filter 16x20x1', 'AF-16201', 'Filters', 12.99, 50, 10, 'HVAC Supply Co'),
            ('Thermostat Digital', 'THERM-DIG-001', 'Controls', 89.99, 15, 5, 'Controls Plus'),
            ('Refrigerant R410A (1lb)', 'REF-410A-1', 'Refrigerant', 25.50, 25, 5, 'Cool Supply')
        ]
        cursor.executemany("""
            INSERT INTO parts (name, part_number, category, unit_cost, quantity_in_stock, reorder_level, supplier)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, parts)

    except sqlite3.Error as e:
        print(f"Error inserting sample data: {e}")
