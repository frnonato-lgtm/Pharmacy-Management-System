import sqlite3
import os

# Get the folder where this file is, so the DB is always created here
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "pharmacy.db")

# Connect to SQLite
def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row # Lets us access data by column name
    return conn

# Setup the tables
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table with all the personal details
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

    # Create medicines table for inventory
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

    # Create prescriptions table
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

    # Create invoices table
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

    # Check if we already have an admin. If not, add default accounts.
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        print("Adding default users...")
        users = [
            ('admin', 'admin123', 'Admin', 'System Admin', ''),
            ('pharm', 'pharm123', 'Pharmacist', 'Carl Renz', 'Colico'),
            ('inv', 'inv123', 'Inventory', 'Kenji Nathaniel', 'David'),
            ('bill', 'bill123', 'Billing', 'Francis Gabriel', 'Nonato'),
            ('staff', 'staff123', 'Staff', 'Staff Member', ''),
            ('pat', 'pat123', 'Patient', 'John', 'Doe')
        ]
        # Insert the users
        cursor.executemany("""
            INSERT INTO users (username, password, role, full_name, last_name) 
            VALUES (?, ?, ?, ?, ?)
        """, users)

        # Add some sample medicines for the inventory
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

# Upgrade existing database to add missing columns
def upgrade_database():
    """Add missing columns to existing tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check and add created_at to users table
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [col[1] for col in cursor.fetchall()]
        
        if 'created_at' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            print("✓ Added created_at column to users table")
        
        # Check and add created_at to medicines table
        cursor.execute("PRAGMA table_info(medicines)")
        medicine_columns = [col[1] for col in cursor.fetchall()]
        
        if 'created_at' not in medicine_columns:
            cursor.execute("ALTER TABLE medicines ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            print("✓ Added created_at column to medicines table")
        
        if 'supplier' not in medicine_columns:
            cursor.execute("ALTER TABLE medicines ADD COLUMN supplier TEXT")
            print("✓ Added supplier column to medicines table")
        
        # Create prescriptions table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                image_path TEXT,
                status TEXT DEFAULT 'Pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users(id)
            )
        """)
        
        # Create invoices table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                patient_id INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'Unpaid',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        print("✓ Database upgrade completed successfully!")
        
    except Exception as e:
        print(f"✗ Error upgrading database: {e}")
        conn.rollback()
    finally:
        conn.close()

# Check if username and password are correct
def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Initialize database (call this when app starts)
def initialize_database():
    """Initialize and upgrade database."""
    init_db()
    upgrade_database()