"""
Complete Database Migration & Seeding Script.
Run this ONCE to update your existing database with all missing tables AND populate it with medicines.
Includes: Pharmacist features + Staff/Patient features + Billing features + 54 Medicines + Sample Transactions.
"""

import sqlite3
import os
import sys
from datetime import datetime

# --- FIX: Add the parent directory to system path so we can import 'services' ---
# This is needed because we are running this script directly from the services folder
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
# -------------------------------------------------------------------------------

from services.database import init_db

def run_migration_and_seed():
    """Add all necessary fields, tables, AND seed data to existing database."""
    
    # 1. Ensure base tables exist first
    print("🔄 Initializing base database structures...")
    init_db()
    
    # Get the correct path to your database
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, 'storage')
    DB_FILE = os.path.join(DB_PATH, "pharmacy.db")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        print("🔄 Starting complete database migration & seeding...\n")
        
        # ============================================
        # PART 1: PHARMACIST FEATURES
        # ============================================
        print("📋 Part 1: Pharmacist Features")
        print("-" * 50)
        
        # 1. Create activity_log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("✅ Activity log table created")
        
        # 2. Add missing fields to prescriptions table
        cursor.execute("PRAGMA table_info(prescriptions)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        # Add new columns if they are missing
        if 'medicine_id' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN medicine_id INTEGER")
            print("✅ Added medicine_id column to prescriptions")
        
        if 'dosage' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN dosage TEXT")
            print("✅ Added dosage column to prescriptions")
        
        if 'frequency' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN frequency TEXT")
            print("✅ Added frequency column to prescriptions")
        
        if 'duration' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN duration INTEGER")
            print("✅ Added duration column to prescriptions")
        
        if 'doctor_name' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN doctor_name TEXT")
            print("✅ Added doctor_name column to prescriptions")
        
        if 'pharmacist_id' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN pharmacist_id INTEGER")
            print("✅ Added pharmacist_id column to prescriptions")
        
        if 'pharmacist_notes' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN pharmacist_notes TEXT")
            print("✅ Added pharmacist_notes column to prescriptions")
        
        if 'reviewed_date' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN reviewed_date TIMESTAMP")
            print("✅ Added reviewed_date column to prescriptions")
        
        # ============================================
        # PART 2: STAFF/PATIENT FEATURES (ORDERS)
        # ============================================
        print("\n📋 Part 2: Orders & Shopping Features")
        print("-" * 50)
        
        # 3. Create orders table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'Pending',
                    total_amount REAL NOT NULL,
                    payment_method TEXT,
                    payment_status TEXT DEFAULT 'Unpaid',
                    notes TEXT,
                    FOREIGN KEY (patient_id) REFERENCES users(id)
                )
            """)
            print("✅ Orders table created")
        else:
            print("✅ Orders table already exists")
        
        # 4. Create order_items table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='order_items'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    medicine_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (medicine_id) REFERENCES medicines(id)
                )
            """)
            print("✅ Order_items table created")
        else:
            print("✅ Order_items table already exists")
        
        # ============================================
        # PART 3: BILLING FEATURES (Enhanced)
        # ============================================
        print("\n📋 Part 3: Billing Features")
        print("-" * 50)
        
        # 5. Check if invoices table needs updates
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invoices'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT UNIQUE NOT NULL,
                    patient_id INTEGER NOT NULL,
                    order_id INTEGER,
                    subtotal REAL NOT NULL,
                    tax REAL DEFAULT 0,
                    discount REAL DEFAULT 0,
                    total_amount REAL NOT NULL,
                    status TEXT DEFAULT 'Unpaid',
                    payment_method TEXT,
                    payment_date TIMESTAMP,
                    billing_clerk_id INTEGER,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES users(id),
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (billing_clerk_id) REFERENCES users(id)
                )
            """)
            print("✅ Invoices table created with full billing features")
        else:
            # Add missing columns to existing invoices table
            cursor.execute("PRAGMA table_info(invoices)")
            invoice_columns = [col[1] for col in cursor.fetchall()]
            
            if 'order_id' not in invoice_columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN order_id INTEGER")
                print("✅ Added order_id to invoices")
            
            if 'subtotal' not in invoice_columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN subtotal REAL DEFAULT 0")
                print("✅ Added subtotal to invoices")
            
            if 'tax' not in invoice_columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN tax REAL DEFAULT 0")
                print("✅ Added tax to invoices")
            
            if 'discount' not in invoice_columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN discount REAL DEFAULT 0")
                print("✅ Added discount to invoices")
            
            if 'payment_method' not in invoice_columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN payment_method TEXT")
                print("✅ Added payment_method to invoices")
            
            if 'payment_date' not in invoice_columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN payment_date TIMESTAMP")
                print("✅ Added payment_date to invoices")
            
            if 'billing_clerk_id' not in invoice_columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN billing_clerk_id INTEGER")
                print("✅ Added billing_clerk_id to invoices")
            
            if 'notes' not in invoice_columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN notes TEXT")
                print("✅ Added notes to invoices")
        
        # 6. Create payments tracking table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payments'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_method TEXT NOT NULL,
                    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    transaction_id TEXT,
                    processed_by INTEGER,
                    notes TEXT,
                    FOREIGN KEY (invoice_id) REFERENCES invoices(id),
                    FOREIGN KEY (processed_by) REFERENCES users(id)
                )
            """)
            print("✅ Payments table created")
        else:
            print("✅ Payments table already exists")
        
        # ============================================
        # PART 4: SEEDING MEDICINES (54 Items)
        # ============================================
        print("\n📋 Part 4: Seeding Medicines (54 Items)")
        print("-" * 50)

        # Check if medicines already exist to avoid duplicates
        cursor.execute("SELECT COUNT(*) FROM medicines")
        med_count = cursor.fetchone()[0]

        if med_count > 0:
            print(f"⚠️ Database already contains {med_count} medicines. Skipping seed.")
        else:
            print("💊 Adding 54 medicines with varied stock levels...")
            
            # Format: Name, Category, Price (PHP), Stock, Expiry, Supplier
            meds = [
                # --- PAIN RELIEF (Varied Stock) ---
                ('Biogesic 500mg', 'Pain Relief', 5.00, 500, '2027-12-31', 'Unilab'), # Good
                ('Alaxan FR', 'Pain Relief', 11.00, 5, '2026-05-20', 'Unilab'),       # Low Stock
                ('Advil 200mg', 'Pain Relief', 13.50, 0, '2025-11-15', 'Pfizer'),     # Out of Stock
                ('RiteMED Paracetamol 500mg', 'Pain Relief', 3.50, 1000, '2027-01-01', 'RiteMED'),
                ('Medicol Advance 400mg', 'Pain Relief', 8.50, 8, '2026-08-10', 'Unilab'), # Low Stock
                ('Dolfenal 500mg', 'Pain Relief', 16.00, 150, '2025-12-05', 'Unilab'),
                ('Ponstan 500mg', 'Pain Relief', 29.00, 100, '2026-03-30', 'Pfizer'),
                ('Flanax 275mg', 'Pain Relief', 19.00, 0, '2026-07-22', 'Bayer'),     # Out of Stock
                ('Tempra Forte Tablet', 'Pain Relief', 6.50, 400, '2026-09-15', 'Taisho'),
                ('Calpol 500mg Tablet', 'Pain Relief', 7.00, 3, '2026-10-01', 'GSK'), # Low Stock
                ('Rexidol 500mg', 'Pain Relief', 5.00, 200, '2026-02-14', 'Unilab'),
                ('Saridon', 'Pain Relief', 6.00, 150, '2026-06-20', 'Bayer'),

                # --- COUGH & COLD (Varied Stock) ---
                ('Neozep Forte', 'Cough & Cold', 6.00, 600, '2026-02-28', 'Unilab'),
                ('Bioflu', 'Cough & Cold', 8.00, 500, '2026-04-15', 'Unilab'),
                ('Solmux 500mg', 'Cough & Cold', 13.00, 9, '2025-12-12', 'Unilab'),   # Low Stock
                ('Decolgen Forte', 'Cough & Cold', 7.50, 400, '2026-01-20', 'Unilab'),
                ('Tuseran Forte', 'Cough & Cold', 10.00, 0, '2026-06-30', 'Unilab'),  # Out of Stock
                ('Robitussin Capsule', 'Cough & Cold', 18.00, 150, '2025-10-10', 'Pfizer'),
                ('Ascof Lagundi 600mg', 'Cough & Cold', 12.00, 200, '2026-03-15', 'Pascual Lab'),
                ('Symdex-D', 'Cough & Cold', 6.00, 500, '2026-11-20', 'Unilab'),
                ('Sinutab High Potency', 'Cough & Cold', 11.50, 150, '2025-09-05', 'J&J'),
                ('RiteMED Ambroxol', 'Cough & Cold', 4.50, 4, '2027-02-14', 'RiteMED'), # Low Stock
                ('Allerkapt (Cetirizine)', 'Cough & Cold', 15.00, 200, '2026-08-20', 'Unilab'),
                ('Virlix 10mg', 'Cough & Cold', 35.00, 100, '2026-09-30', 'GSK'),

                # --- ANTIBIOTICS (Mostly Good Stock) ---
                ('Amoxil 500mg', 'Antibiotics', 28.00, 100, '2025-08-30', 'GSK'),
                ('Augmentin 625mg', 'Antibiotics', 85.00, 50, '2025-07-15', 'GSK'),
                ('RiteMED Amoxicillin', 'Antibiotics', 9.00, 500, '2026-05-01', 'RiteMED'),
                ('Zithromax (Azithromycin)', 'Antibiotics', 120.00, 2, '2025-12-31', 'Pfizer'), # Low Stock
                ('RiteMED Cephalexin', 'Antibiotics', 18.00, 200, '2026-01-10', 'RiteMED'),
                ('Ciprobay 500mg', 'Antibiotics', 65.00, 150, '2026-04-20', 'Bayer'),
                
                # --- MAINTENANCE (Varied) ---
                ('Norvasc 5mg', 'Maintenance', 33.00, 200, '2026-11-11', 'Pfizer'),
                ('Lipitor 10mg', 'Maintenance', 45.00, 0, '2026-10-25', 'Pfizer'),    # Out of Stock
                ('RiteMED Losartan 50mg', 'Maintenance', 12.00, 500, '2027-01-05', 'RiteMED'),
                ('RiteMED Amlodipine 10mg', 'Maintenance', 9.00, 600, '2027-03-15', 'RiteMED'),
                ('Glucophage 500mg', 'Diabetes', 19.50, 300, '2026-02-20', 'Merck'),
                ('RiteMED Metformin 500mg', 'Diabetes', 6.00, 7, '2027-05-10', 'RiteMED'), # Low Stock
                ('Euglucon 5mg', 'Diabetes', 18.00, 400, '2026-09-09', 'Pfizer'),
                ('Plavix 75mg', 'Heart Health', 90.00, 50, '2025-12-01', 'Sanofi'),

                # --- VITAMINS (Varied) ---
                ('Enervon C', 'Vitamins', 8.00, 500, '2027-01-01', 'Unilab'),
                ('Centrum Advance', 'Vitamins', 14.00, 200, '2026-08-15', 'Pfizer'),
                ('Poten-Cee 500mg', 'Vitamins', 7.50, 0, '2026-12-10', 'Pascual Lab'), # Out of Stock
                ('Stresstabs', 'Vitamins', 12.00, 150, '2026-05-30', 'Pfizer'),
                ('Myra E 400IU', 'Vitamins', 15.00, 200, '2026-02-14', 'Unilab'),
                ('Fern-C', 'Vitamins', 9.00, 5, '2026-07-20', 'Fern'), # Low Stock
                ('Immunpro', 'Vitamins', 17.00, 100, '2026-04-05', 'Unilab'),
                ('Neurogen-E', 'Vitamins', 24.00, 150, '2026-06-15', 'Unilab'),

                # --- GASTRO (Varied) ---
                ('Kremil-S', 'Antacid', 6.00, 500, '2027-02-28', 'Unilab'),
                ('Gaviscon Double Action', 'Antacid', 32.00, 6, '2026-01-20', 'Reckitt'), # Low Stock
                ('Imodium 2mg', 'Antidiarrheal', 22.00, 200, '2026-11-30', 'J&J'),
                ('Diatabs', 'Antidiarrheal', 9.00, 300, '2027-03-10', 'Unilab'),
                ('Buscopan 10mg', 'Antispasmodic', 25.00, 150, '2026-08-05', 'Sanofi'),
                ('Erceflora 2B', 'Probiotics', 55.00, 0, '2025-10-15', 'Sanofi'),      # Out of Stock
                ('RiteMED Omeprazole 20mg', 'Antacid', 15.00, 400, '2026-12-05', 'RiteMED'),
                ('Motilium 10mg', 'Antinausea', 35.00, 50, '2025-09-20', 'J&J'),
            ]
            
            # Insert into database
            cursor.executemany("""
                INSERT INTO medicines (name, category, price, stock, expiry_date, supplier) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, meds)
            
            print("✅ Success! 54 Medicines added.")

        # ============================================
        # PART 5: DATABASE INDEXES (Performance)
        # ============================================
        print("\n📋 Part 5: Database Indexes")
        print("-" * 50)
        
        # Activity log indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_log(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_log(timestamp)")
        
        # Prescription indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prescriptions_status ON prescriptions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prescriptions_patient ON prescriptions(patient_id)")
        
        # Order indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_patient ON orders(patient_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id)")
        
        # Billing indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_patient ON invoices(patient_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_number ON invoices(invoice_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_invoice ON payments(invoice_id)")
        
        print("✅ All database indexes created")

        # ============================================
        # PART 6: SAMPLE TRANSACTIONS (Prescriptions/Orders)
        # ============================================
        print("\n📋 Part 6: Sample Transactions")
        print("-" * 50)
        
        # Add sample prescriptions if they don't exist
        cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE medicine_id IS NOT NULL")
        if cursor.fetchone()[0] == 0:
            print("📝 Adding sample prescriptions...")
            
            # Get patient ID
            cursor.execute("SELECT id FROM users WHERE username = 'pat'")
            patient = cursor.fetchone()
            patient_id = patient[0] if patient else 1
            
            # Get some medicine IDs
            cursor.execute("SELECT id FROM medicines LIMIT 4")
            medicine_ids = [row[0] for row in cursor.fetchall()]
            
            if medicine_ids:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Format: patient_id, medicine_id, status, dosage, frequency, duration, doctor_name, notes, created_at
                sample_prescriptions = [
                    (patient_id, medicine_ids[0], 'Pending', '500mg', '3 times daily', 7, 'Dr. Smith', 'Patient has penicillin allergy', now),
                    (patient_id, medicine_ids[1] if len(medicine_ids) > 1 else medicine_ids[0], 'Pending', '250mg', '2 times daily', 5, 'Dr. Johnson', 'Take with food', now),
                    (patient_id, medicine_ids[2] if len(medicine_ids) > 2 else medicine_ids[0], 'Approved', '400mg', 'Every 8 hours', 10, 'Dr. Williams', 'Approved for dispensing', now),
                    (patient_id, medicine_ids[3] if len(medicine_ids) > 3 else medicine_ids[0], 'Pending', '10mg', 'Once daily', 14, 'Dr. Brown', 'Monitor for side effects', now),
                ]
                
                cursor.executemany("""
                    INSERT INTO prescriptions 
                    (patient_id, medicine_id, status, dosage, frequency, duration, doctor_name, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, sample_prescriptions)
                print(f"✅ Added {len(sample_prescriptions)} sample prescriptions")
        else:
            print("✅ Prescriptions table already has data")
        
        # Add sample orders if they don't exist
        cursor.execute("SELECT COUNT(*) FROM orders")
        if cursor.fetchone()[0] == 0:
            print("📝 Adding sample orders...")
            
            cursor.execute("SELECT id FROM users WHERE username = 'pat'")
            patient = cursor.fetchone()
            patient_id = patient[0] if patient else 1
            
            cursor.execute("SELECT id, price FROM medicines LIMIT 3")
            medicines = cursor.fetchall()
            
            if medicines:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Create sample order header
                cursor.execute("""
                    INSERT INTO orders (patient_id, order_date, status, total_amount, payment_method, payment_status, notes)
                    VALUES (?, ?, 'Completed', 150.00, 'Cash', 'Paid', 'Sample order')
                """, (patient_id, now))
                
                order_id = cursor.lastrowid
                
                # Add order items (2 items from the first 2 medicines found)
                for med in medicines[:2]:
                    cursor.execute("""
                        INSERT INTO order_items (order_id, medicine_id, quantity, unit_price, subtotal)
                        VALUES (?, ?, 2, ?, ?)
                    """, (order_id, med[0], med[1], med[1] * 2))
                
                print("✅ Added 1 sample order with 2 items")
        else:
            print("✅ Orders table already has data")
        
        # ============================================
        # COMMIT CHANGES
        # ============================================
        conn.commit()
        
        print("\n" + "=" * 50)
        print("🎉 MIGRATION & SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("\n📋 Summary:")
        print("   ✅ Activity log table created")
        print("   ✅ All tables (Orders, Invoices, Prescriptions) verified")
        print("   ✅ 54 Medicines seeded (with varied stock levels)")
        print("   ✅ Performance indexes added")
        print("   ✅ Sample Transactions (Rx/Orders) added")
        print("\n✨ You can now run 'python main.py'!")
        print("=" * 50 + "\n")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during migration: {e}")
        print("   Please check the error and try again.")
        import traceback
        traceback.print_exc()
        
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration_and_seed()