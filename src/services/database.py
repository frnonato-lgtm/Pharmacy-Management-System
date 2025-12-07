import sqlite3
import os

# Figure out where this file is, so we can put the DB in the same folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'storage')

# Make sure the storage folder exists
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

DB_FILE = os.path.join(DB_PATH, "pharmacy.db")

# Helper to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row # This lets us use column names like row['name']
    return conn

# Setup the tables if they don't exist
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table for all users
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

    # Table for medicines
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
            medicine_id INTEGER,
            dosage TEXT,
            frequency TEXT,
            duration INTEGER,
            doctor_name TEXT,
            pharmacist_id INTEGER,
            pharmacist_notes TEXT,
            reviewed_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(id)
        )
    ''')

    # Table for invoices
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            patient_id INTEGER NOT NULL,
            order_id INTEGER,
            subtotal REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            discount REAL DEFAULT 0,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'Unpaid',
            payment_method TEXT,
            payment_date TIMESTAMP,
            billing_clerk_id INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(id)
        )
    ''')

    # Create default admin if the system is fresh (first run)
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        print("Adding default test users...")
        users = [
            ('admin', 'admin123', 'Admin', 'System Admin', ''),
            ('pharm', 'pharm123', 'Pharmacist', 'Carl Renz', 'Colico'),
            ('inv', 'inv123', 'Inventory', 'Kenji Nathaniel', 'David'),
            ('bill', 'bill123', 'Billing', 'Francis Gabriel', 'Nonato'),
            ('staff', 'staff123', 'Staff', 'Staff Member', ''),
        ]
        cursor.executemany("""
            INSERT INTO users (username, password, role, full_name, last_name) 
            VALUES (?, ?, ?, ?, ?)
        """, users)

        # Adding 50 medicines commonly found in PH pharmacies
        print("Seeding database with 50 medicines...")
        meds = [
            # Pain Relief
            ('Biogesic 500mg', 'Pain Relief', 5.00, 500, '2026-12-31', 'Unilab'),
            ('Alaxan FR', 'Pain Relief', 10.00, 300, '2026-05-20', 'Unilab'),
            ('Advil 200mg', 'Pain Relief', 11.00, 200, '2025-11-15', 'Pfizer'),
            ('RiteMED Paracetamol', 'Pain Relief', 3.00, 1000, '2027-01-01', 'RiteMED'),
            ('Medicol Advance', 'Pain Relief', 8.00, 250, '2026-08-10', 'Unilab'),
            ('Dolfenal 500mg', 'Pain Relief', 15.00, 150, '2025-12-05', 'Unilab'),
            ('Ponstan 500mg', 'Pain Relief', 25.00, 100, '2026-03-30', 'Pfizer'),
            ('Flanax 275mg', 'Pain Relief', 18.00, 120, '2026-07-22', 'Bayer'),
            ('Tempra Forte', 'Pain Relief', 6.00, 400, '2026-09-15', 'Taisho'),
            ('Calpol 500mg', 'Pain Relief', 7.00, 350, '2026-10-01', 'GSK'),

            # Cough & Cold
            ('Neozep Forte', 'Cough & Cold', 6.00, 600, '2026-02-28', 'Unilab'),
            ('Bioflu', 'Cough & Cold', 7.50, 500, '2026-04-15', 'Unilab'),
            ('Solmux 500mg', 'Cough & Cold', 12.00, 300, '2025-12-12', 'Unilab'),
            ('Decolgen Forte', 'Cough & Cold', 6.50, 400, '2026-01-20', 'Unilab'),
            ('Tuseran Forte', 'Cough & Cold', 8.00, 300, '2026-06-30', 'Unilab'),
            ('Robitussin Capsule', 'Cough & Cold', 15.00, 150, '2025-10-10', 'Pfizer'),
            ('Ascof Lagundi', 'Cough & Cold', 10.00, 200, '2026-03-15', 'Pascual Lab'),
            ('Symdex-D', 'Cough & Cold', 5.00, 500, '2026-11-20', 'Unilab'),
            ('Sinutab High Potency', 'Cough & Cold', 10.00, 150, '2025-09-05', 'J&J'),
            ('Ambroxol RiteMED', 'Cough & Cold', 4.00, 800, '2027-02-14', 'RiteMED'),

            # Antibiotics (Prescription)
            ('Amoxil 500mg', 'Antibiotics', 25.00, 100, '2025-08-30', 'GSK'),
            ('Augmentin 625mg', 'Antibiotics', 45.00, 50, '2025-07-15', 'GSK'),
            ('RiteMED Amoxicillin', 'Antibiotics', 8.00, 500, '2026-05-01', 'RiteMED'),
            ('Azithromycin 500mg', 'Antibiotics', 50.00, 40, '2025-12-31', 'Generic'),
            ('Cephalexin 500mg', 'Antibiotics', 15.00, 200, '2026-01-10', 'Generic'),
            ('Ciprofloxacin 500mg', 'Antibiotics', 18.00, 150, '2026-04-20', 'Generic'),
            
            # Maintenance / Heart / Diabetes
            ('Norvasc 5mg', 'Maintenance', 20.00, 200, '2026-11-11', 'Pfizer'),
            ('Lipitor 10mg', 'Maintenance', 25.00, 150, '2026-10-25', 'Pfizer'),
            ('Losartan 50mg', 'Maintenance', 10.00, 500, '2027-01-05', 'RiteMED'),
            ('Amlodipine 10mg', 'Maintenance', 8.00, 600, '2027-03-15', 'RiteMED'),
            ('Glucophage 500mg', 'Diabetes', 18.00, 300, '2026-02-20', 'Merck'),
            ('Metformin 500mg', 'Diabetes', 5.00, 800, '2027-05-10', 'RiteMED'),
            ('Glibenclamide 5mg', 'Diabetes', 6.00, 400, '2026-09-09', 'RiteMED'),
            ('Plavix 75mg', 'Heart Health', 55.00, 50, '2025-12-01', 'Sanofi'),

            # Supplements / Vitamins
            ('Enervon C', 'Vitamins', 7.00, 500, '2027-01-01', 'Unilab'),
            ('Centrum Advance', 'Vitamins', 12.00, 200, '2026-08-15', 'Pfizer'),
            ('Poten-Cee 500mg', 'Vitamins', 6.00, 400, '2026-12-10', 'Pascual Lab'),
            ('Stresstabs', 'Vitamins', 11.00, 150, '2026-05-30', 'Pfizer'),
            ('Myra E 400IU', 'Vitamins', 13.00, 200, '2026-02-14', 'Unilab'),
            ('Fern-C', 'Vitamins', 8.00, 300, '2026-07-20', 'Fern'),
            ('Immunpro', 'Vitamins', 15.00, 100, '2026-04-05', 'Unilab'),
            ('Neurogen-E', 'Vitamins', 20.00, 150, '2026-06-15', 'Unilab'),

            # Gastric / Stomach
            ('Kremil-S', 'Antacid', 5.00, 500, '2027-02-28', 'Unilab'),
            ('Gaviscon Double Action', 'Antacid', 25.00, 100, '2026-01-20', 'Reckitt'),
            ('Imodium 2mg', 'Antidiarrheal', 18.00, 200, '2026-11-30', 'J&J'),
            ('Diatabs', 'Antidiarrheal', 8.00, 300, '2027-03-10', 'Unilab'),
            ('Buscopan 10mg', 'Antispasmodic', 22.00, 150, '2026-08-05', 'Sanofi'),
            ('Erceflora', 'Probiotics', 40.00, 80, '2025-10-15', 'Sanofi'),
            ('Omeprazole 20mg', 'Antacid', 12.00, 400, '2026-12-05', 'RiteMED'),
            ('Motilium', 'Antinausea', 30.00, 50, '2025-09-20', 'J&J'),
        ]
        
        cursor.executemany("""
            INSERT INTO medicines (name, category, price, stock, expiry_date, supplier) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, meds)

    conn.commit()
    conn.close()

# Check login credentials
def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user