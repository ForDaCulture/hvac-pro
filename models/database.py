# models/database.py

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
    Initialize the SQLite database with all required tables.
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
            preferred_time TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            hourly_rate DECIMAL(10,2) DEFAULT 35.00,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Jobs table
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
            status VARCHAR(20) DEFAULT 'scheduled',
            notes TEXT,
            completed_at TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (technician_id) REFERENCES technicians (id)
        )
    """)

    # --- Insert Sample Data (only if customers table is empty) ---
    cursor.execute('SELECT COUNT(id) FROM customers')
    if cursor.fetchone()[0] == 0:
        insert_sample_data(cursor)

    conn.commit()
    conn.close()

def insert_sample_data(cursor):
    """Inserts sample data for customers and technicians."""
    customers = [
        ('John Smith', '555-0101', 'john@example.com', '123 Main St, Nashua, NH', '["morning"]'),
        ('Sarah Johnson', '555-0102', 'sarah@example.com', '456 Oak Ave, Nashua, NH', '["afternoon"]')
    ]
    cursor.executemany("INSERT INTO customers (name, phone, email, address, preferred_time) VALUES (?, ?, ?, ?, ?)", customers)

    technicians = [
        ('Bob Martinez', '555-0201', 'bob@hvacpro.com', '["residential", "commercial"]', '{}', 45.00),
        ('Lisa Chen', '555-0202', 'lisa@hvacpro.com', '["residential", "electrical"]', '{}', 40.00)
    ]
    cursor.executemany("INSERT INTO technicians (name, phone, email, skills, availability, hourly_rate) VALUES (?, ?, ?, ?, ?, ?)", technicians)