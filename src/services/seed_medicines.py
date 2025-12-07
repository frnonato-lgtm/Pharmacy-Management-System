"""
RUN THIS SCRIPT ONCE to add the medicines to your database.
Includes 54 medicines with varied stock levels (Good, Low, Out of Stock).
"""
from database import get_db_connection, init_db

def seed_medicines():
    # 1. Initialize the tables first
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # 2. Check if data exists
    cursor.execute("SELECT COUNT(*) FROM medicines")
    count = cursor.fetchone()[0]

    if count > 0:
        print(f"Database already contains {count} medicines. Skipping seed.")
        conn.close()
        return

    print("Adding 54 medicines with varied stock levels...")

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
    
    # 3. Insert into database
    cursor.executemany("""
        INSERT INTO medicines (name, category, price, stock, expiry_date, supplier) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, meds)

    conn.commit()
    conn.close()
    print("Success! 54 Medicines added with varied stock levels.")

if __name__ == "__main__":
    seed_medicines()