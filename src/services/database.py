import sqlite3
import os
import json
import urllib.request

# Custom Turso Client (No external dependencies, 3.14 compatible)
class LibsqlRow:
    def __init__(self, columns, values):
        self._data = dict(zip(columns, values))
        self._values = values
    def __getitem__(self, key):
        if isinstance(key, int): return self._values[key]
        return self._data[key]
    def keys(self): return list(self._data.keys())

class LibsqlCursor:
    def __init__(self, conn):
        self.conn = conn
        self.result_rows = []
        self.columns = []
        self.index = 0
    
    def execute(self, sql, params=()):
        # Convert params to Turso format
        p = []
        for val in params:
            if isinstance(val, int): p.append({"type": "integer", "value": str(val)})
            elif isinstance(val, float): p.append({"type": "float", "value": val})
            elif val is None: p.append({"type": "null"})
            else: p.append({"type": "text", "value": str(val)})

        payload = {"requests": [{"type": "execute", "stmt": {"sql": sql, "args": p}}]}
        
        req = urllib.request.Request(
            self.conn.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.conn.token}", "Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode("utf-8"))
            exec_res = data["results"][0]["response"]["result"]
            self.columns = [c["name"] for c in exec_res["cols"]]
            self.rowcount = exec_res.get("affected_row_count", 0)
            self.result_rows = []
            for r in exec_res["rows"]:
                self.result_rows.append([v.get("value") for v in r])
            self.index = 0
        return self

    def executemany(self, sql, param_list):
        for params in param_list:
            self.execute(sql, params)
        return self

    def fetchone(self):
        if self.index >= len(self.result_rows): return None
        row = self.result_rows[self.index]
        self.index += 1
        if self.conn.row_factory == sqlite3.Row:
            return LibsqlRow(self.columns, row)
        return row

    def fetchall(self):
        return [self.fetchone() for _ in range(len(self.result_rows) - self.index)]

class LibsqlConnection:
    def __init__(self, url, token):
        # Normalize URL to pipeline
        api_url = url.replace("libsql://", "https://")
        if not api_url.endswith("/v2/pipeline"):
            api_url = f"{api_url.rstrip('/')}/v2/pipeline"
        self.api_url = api_url
        self.token = token
        self.row_factory = None
    def cursor(self): return LibsqlCursor(self)
    def commit(self): pass
    def close(self): pass

# Resolve absolute path for database persistence
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'storage')

# Verify persistence directory exists
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

DB_FILE = os.path.join(DB_PATH, "pharmacy.db")

# Initialize database connection (supports Turso and local SQLite)
def get_db_connection():
    # Check for Turso Environment Variables
    turso_url = os.environ.get("TURSO_DATABASE_URL")
    turso_token = os.environ.get("TURSO_AUTH_TOKEN")

    if turso_url and turso_token:
        # Use our custom 3.14-friendly HTTP client
        return LibsqlConnection(turso_url, turso_token)
    else:
        # Fallback to Local SQLite
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn


# Execute database schema migration
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Schema: Users
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
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Legacy schema migration for status column
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'Pending'")
    except sqlite3.OperationalError:
        pass # Column already defined

    # Schema: Medicines
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

    # Schema: Prescriptions
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

    # Schema: Invoices
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

    # Schema: Cart
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(id),
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    ''')

    # Schema: Orders
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Pending',
            total_amount REAL NOT NULL,
            payment_method TEXT,
            notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES users(id)
        )
    ''')

    # Schema: Order Items
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    ''')

    # Schema: Activity Log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Provision default system accounts
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        users = [
            ('admin', 'admin123', 'Admin', 'System Admin', '', 'Approved'),
            ('pharm', 'pharm123', 'Pharmacist', 'Carl Renz', 'Colico', 'Approved'),
            ('inv', 'inv123', 'Inventory', 'Kenji Nathaniel', 'David', 'Approved'),
            ('bill', 'bill123', 'Billing', 'Francis Gabriel', 'Nonato', 'Approved'),
            ('staff', 'staff123', 'Staff', 'Staff Member', '', 'Approved'),
            ('pat', 'pat123', 'Patient', 'John', 'Doe', 'Approved')
        ]
        cursor.executemany("""
            INSERT INTO users (username, password, role, full_name, last_name, status) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, users)

    # Automatically approve provisioned system accounts
    cursor.execute("UPDATE users SET status = 'Approved' WHERE status IS NULL OR status = 'Pending' AND username IN ('admin', 'pharm', 'inv', 'bill', 'staff', 'pat')")

    conn.commit()
    conn.close()

# Authenticate user credentials
def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user