"""
Database migration to add missing fields for pharmacist functionality.
Run this ONCE to update your existing database.
Place this in: src/services/db_migration.py
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Add necessary fields to existing database."""
    
    # Get the correct path to your database
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, 'storage')
    DB_FILE = os.path.join(DB_PATH, "pharmacy.db")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        print("🔄 Starting database migration...")
        
        # 1. Create activity_log table for tracking pharmacist actions
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
        # Check which columns exist first
        cursor.execute("PRAGMA table_info(prescriptions)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        # Add medicine_id if it doesn't exist
        if 'medicine_id' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN medicine_id INTEGER")
            print("✅ Added medicine_id column")
        
        if 'dosage' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN dosage TEXT")
            print("✅ Added dosage column")
        
        if 'frequency' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN frequency TEXT")
            print("✅ Added frequency column")
        
        if 'duration' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN duration INTEGER")
            print("✅ Added duration column")
        
        if 'doctor_name' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN doctor_name TEXT")
            print("✅ Added doctor_name column")
        
        # Add pharmacist review fields if they don't exist
        if 'pharmacist_id' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN pharmacist_id INTEGER")
            print("✅ Added pharmacist_id column")
        
        if 'pharmacist_notes' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN pharmacist_notes TEXT")
            print("✅ Added pharmacist_notes column")
        
        if 'reviewed_date' not in existing_columns:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN reviewed_date TIMESTAMP")
            print("✅ Added reviewed_date column")
        
        # 3. Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_user 
            ON activity_log(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_timestamp 
            ON activity_log(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prescriptions_status 
            ON prescriptions(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prescriptions_patient 
            ON prescriptions(patient_id)
        """)
        print("✅ Created database indexes")
        
        # 4. Add some sample prescriptions if the table is empty or has only old records
        cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE medicine_id IS NOT NULL")
        if cursor.fetchone()[0] == 0:
            print("📝 Adding sample prescriptions...")
            
            # Get patient ID (assuming 'pat' user exists)
            cursor.execute("SELECT id FROM users WHERE username = 'pat'")
            patient = cursor.fetchone()
            patient_id = patient[0] if patient else 1
            
            # Get some medicine IDs
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
        
        conn.commit()
        print("\n🎉 Migration completed successfully!")
        print("\n📋 Summary:")
        print("   - Activity log table created")
        print("   - Prescription fields updated")
        print("   - Database indexes created")
        print("   - Sample data added (if needed)")
        print("\n✅ You can now use the pharmacist features!")
        
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