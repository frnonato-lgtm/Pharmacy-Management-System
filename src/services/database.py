import sqlite3
import os

# Figure out where this file is, so we can save the DB in the 'storage' folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'storage')

# Create the storage folder if it doesn't exist yet
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

DB_FILE = os.path.join(DB_PATH, "pharmacy.db")

# Helper to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row # Allows us to access columns by name
    return conn

# Setup the database tables
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table for all users (Admin, Patient, Staff, etc.)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT,
            last_name TEXT,
            email TEXT,
            phone TEXT,
            dob TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table for medicines inventory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER,
            expiry_date TEXT,
            supplier TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table for prescriptions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            image_path TEXT,
            status TEXT DEFAULT 'Pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(id)
        )
    ''')

    # Table for billing invoices
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            patient_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'Unpaid',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(id)
        )
    ''')

    # Add default test accounts if the database is empty
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        print("Adding default test users...")
        users = [
            ('admin', 'admin123', 'Admin', 'System Admin', ''),
            ('pharm', 'pharm123', 'Pharmacist', 'Carl Renz', 'Colico'),
            ('inv', 'inv123', 'Inventory', 'Kenji Nathaniel', 'David'),
            ('bill', 'bill123', 'Billing', 'Francis Gabriel', 'Nonato'),
            ('staff', 'staff123', 'Staff', 'Staff Member', ''),
            ('pat', 'pat123', 'Patient', 'John', 'Doe')
        ]
        cursor.executemany("""
            INSERT INTO users (username, password, role, full_name, last_name) 
            VALUES (?, ?, ?, ?, ?)
        """, users)

        # Add sample medicines
        meds = [
            ('Paracetamol', 'Pain Relief', 5.00, 100, '2026-01-01', 'PharmaCorp'),
            ('Amoxicillin', 'Antibiotic', 15.00, 50, '2025-12-01', 'MediSupply'),
            ('Vitamin C', 'Supplement', 8.00, 5, '2025-06-01', 'HealthPlus'),
            ('Ibuprofen', 'Pain Relief', 7.50, 200, '2026-05-20', 'PharmaCorp')
        ]
        cursor.executemany("""
            INSERT INTO medicines (name, category, price, stock, expiry_date, supplier) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, meds)

    conn.commit()
    conn.close()

# Simple function to check login credentials
def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user