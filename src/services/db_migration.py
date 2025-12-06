"""
Complete Database Migration - All Features
Run this ONCE to update your existing database with all missing tables.
Includes: Pharmacist features + Staff/Patient features + Billing features
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Add all necessary fields and tables to existing database."""
    
    # Get the correct path to your database
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, 'storage')
    DB_FILE = os.path.join(DB_PATH, "pharmacy.db")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        print("🔄 Starting complete database migration...\n")
        
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
        # PART 4: DATABASE INDEXES (Performance)
        # ============================================
        print("\n📋 Part 4: Database Indexes")
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
        # PART 5: SAMPLE DATA (Optional)
        # ============================================
        print("\n📋 Part 5: Sample Data")
        print("-" * 50)
        
        # Add sample prescriptions if needed
        cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE medicine_id IS NOT NULL")
        if cursor.fetchone()[0] == 0:
            print("📝 Adding sample prescriptions...")
            
            cursor.execute("SELECT id FROM users WHERE username = 'pat'")
            patient = cursor.fetchone()
            patient_id = patient[0] if patient else 1
            
            cursor.execute("SELECT id FROM medicines LIMIT 4")
            medicine_ids = [row[0] for row in cursor.fetchall()]
            
            if medicine_ids:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            print("✅ Prescriptions table has data")
        
        # Add sample orders if needed
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
                
                # Create sample order
                cursor.execute("""
                    INSERT INTO orders (patient_id, order_date, status, total_amount, payment_method, payment_status, notes)
                    VALUES (?, ?, 'Completed', 150.00, 'Cash', 'Paid', 'Sample order')
                """, (patient_id, now))
                
                order_id = cursor.lastrowid
                
                # Add order items
                for med in medicines[:2]:  # Use first 2 medicines
                    cursor.execute("""
                        INSERT INTO order_items (order_id, medicine_id, quantity, unit_price, subtotal)
                        VALUES (?, ?, 2, ?, ?)
                    """, (order_id, med[0], med[1], med[1] * 2))
                
                print("✅ Added 1 sample order with 2 items")
        else:
            print("✅ Orders table has data")
        
        # ============================================
        # COMMIT CHANGES
        # ============================================
        conn.commit()
        
        print("\n" + "=" * 50)
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("\n📋 Summary:")
        print("   ✅ Activity log table (Pharmacist)")
        print("   ✅ Prescription fields updated (Pharmacist)")
        print("   ✅ Orders table (Staff/Patient)")
        print("   ✅ Order_items table (Staff/Patient)")
        print("   ✅ Invoices table verified (Billing)")
        print("   ✅ Database indexes created (Performance)")
        print("   ✅ Sample data added (Testing)")
        print("\n✨ All features are now ready to use!")
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
    run_migration()