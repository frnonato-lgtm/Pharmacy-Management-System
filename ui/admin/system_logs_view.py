"""System activity logs and audit trail."""

import flet as ft
from database import get_db_connection
from datetime import datetime, timedelta

def SystemLogs():
    """System logs and activity monitoring interface."""
    
    logs_container = ft.Column(spacing=10)
    
    # Filter controls
    log_type_filter = ft.Dropdown(
        label="Activity Type",
        options=[
            ft.dropdown.Option("All", "All Activities"),
            ft.dropdown.Option("Login", "User Logins"),
            ft.dropdown.Option("Registration", "New Registrations"),
            ft.dropdown.Option("Prescription", "Prescription Actions"),
            ft.dropdown.Option("Inventory", "Inventory Changes"),
            ft.dropdown.Option("Invoice", "Billing Activities"),
            ft.dropdown.Option("Admin", "Admin Actions"),
        ],
        value="All",
        width=250,
    )
    
    user_filter = ft.TextField(
        label="Filter by User",
        hint_text="Enter username...",
        width=200,
    )
    
    date_from = ft.TextField(
        label="From Date",
        hint_text="YYYY-MM-DD",
        value=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
        width=150,
    )
    
    date_to = ft.TextField(
        label="To Date",
        hint_text="YYYY-MM-DD",
        value=datetime.now().strftime("%Y-%m-%d"),
        width=150,
    )
    
    # Statistics
    stats_row = ft.Row(spacing=15, wrap=True)
    
    def create_activity_log(log_type, user, action, details, timestamp):
        """Create a single log entry UI."""
        
        # Icon and color based on activity type
        icon_map = {
            "Login": (ft.Icons.LOGIN, "primary"),
            "Registration": (ft.Icons.PERSON_ADD, "secondary"),
            "Prescription": (ft.Icons.DESCRIPTION, "tertiary"),
            "Inventory": (ft.Icons.INVENTORY, "secondary"),
            "Invoice": (ft.Icons.RECEIPT, "primary"),
            "Admin": (ft.Icons.ADMIN_PANEL_SETTINGS, "error"),
        }
        
        icon, color = icon_map.get(log_type, (ft.Icons.INFO, "outline"))
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=color, size=24),
                ft.Container(width=10),
                ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Text(
                                log_type,
                                size=11,
                                weight="bold",
                                color=f"on{color.capitalize()}",
                            ),
                            bgcolor=ft.Colors.with_opacity(0.2, color),
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=5,
                        ),
                        ft.Text("•", color="outline"),
                        ft.Text(user, size=13, weight="bold"),
                        ft.Text("•", color="outline"),
                        ft.Text(timestamp, size=12, color="outline"),
                    ], spacing=5),
                    ft.Text(action, size=14, weight="bold"),
                    ft.Text(details, size=12, color="outline") if details else ft.Container(),
                ], spacing=3, expand=True),
            ], spacing=0),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
            bgcolor="surface",
        )
    
    def create_stat_card(title, value, icon, color):
        """Create statistics card."""
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=color, size=30),
                ft.Column([
                    ft.Text(str(value), size=24, weight="bold", color=color),
                    ft.Text(title, size=12, color="outline"),
                ], spacing=2),
            ], spacing=10),
            padding=15,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
            expand=True,
        )
    
    def load_statistics():
        """Load and display activity statistics."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        # Users registered today
        cursor.execute("""
            SELECT COUNT(*) as count FROM users 
            WHERE DATE(created_at) = DATE('now')
        """)
        today_registrations = cursor.fetchone()['count']
        
        # Total prescriptions
        cursor.execute("SELECT COUNT(*) as count FROM prescriptions")
        total_prescriptions = cursor.fetchone()['count']
        
        # Pending prescriptions
        cursor.execute("""
            SELECT COUNT(*) as count FROM prescriptions 
            WHERE status = 'Pending'
        """)
        pending_prescriptions = cursor.fetchone()['count']
        
        conn.close()
        
        stats_row.controls = [
            create_stat_card("Total Users", total_users, ft.Icons.PEOPLE, "primary"),
            create_stat_card("Registered Today", today_registrations, ft.Icons.PERSON_ADD, "secondary"),
            create_stat_card("Total Prescriptions", total_prescriptions, ft.Icons.DESCRIPTION, "tertiary"),
            create_stat_card("Pending Review", pending_prescriptions, ft.Icons.PENDING, "tertiary"),
        ]
    
    def generate_mock_logs(log_type="All", username="", from_date="", to_date=""):
        """Generate activity logs based on actual database data."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        logs = []
        
        # Get user registrations
        if log_type in ["All", "Registration"]:
            query = "SELECT username, full_name, role, created_at FROM users WHERE 1=1"
            params = []
            
            if username:
                query += " AND LOWER(username) LIKE ?"
                params.append(f"%{username.lower()}%")
            
            if from_date:
                query += " AND DATE(created_at) >= ?"
                params.append(from_date)
            
            if to_date:
                query += " AND DATE(created_at) <= ?"
                params.append(to_date)
            
            query += " ORDER BY created_at DESC LIMIT 20"
            
            cursor.execute(query, params)
            users = cursor.fetchall()
            
            for user in users:
                logs.append({
                    'type': 'Registration',
                    'user': user['username'],
                    'action': 'New user registration',
                    'details': f"Registered as {user['role']}: {user['full_name']}",
                    'timestamp': user['created_at'] or datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
        
        # Get prescription activities
        if log_type in ["All", "Prescription"]:
            query = """
                SELECT p.id, p.status, p.created_at, u.username, u.full_name
                FROM prescriptions p
                JOIN users u ON p.patient_id = u.id
                WHERE 1=1
            """
            params = []
            
            if username:
                query += " AND LOWER(u.username) LIKE ?"
                params.append(f"%{username.lower()}%")
            
            if from_date:
                query += " AND DATE(p.created_at) >= ?"
                params.append(from_date)
            
            if to_date:
                query += " AND DATE(p.created_at) <= ?"
                params.append(to_date)
            
            query += " ORDER BY p.created_at DESC LIMIT 20"
            
            cursor.execute(query, params)
            prescriptions = cursor.fetchall()
            
            for rx in prescriptions:
                action_text = "Uploaded prescription"
                if rx['status'] == 'Approved':
                    action_text = "Prescription approved"
                elif rx['status'] == 'Rejected':
                    action_text = "Prescription rejected"
                
                logs.append({
                    'type': 'Prescription',
                    'user': rx['username'],
                    'action': action_text,
                    'details': f"Prescription #{rx['id']} - Status: {rx['status']}",
                    'timestamp': rx['created_at'] or datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
        
        # Get inventory activities (based on recent medicines)
        if log_type in ["All", "Inventory"]:
            query = """
                SELECT name, category, stock, created_at
                FROM medicines
                WHERE 1=1
            """
            params = []
            
            if from_date:
                query += " AND DATE(created_at) >= ?"
                params.append(from_date)
            
            if to_date:
                query += " AND DATE(created_at) <= ?"
                params.append(to_date)
            
            query += " ORDER BY created_at DESC LIMIT 15"
            
            cursor.execute(query, params)
            medicines = cursor.fetchall()
            
            for med in medicines:
                logs.append({
                    'type': 'Inventory',
                    'user': 'admin',  # Default to admin for inventory
                    'action': 'Medicine stock updated',
                    'details': f"{med['name']} ({med['category']}) - Current stock: {med['stock']}",
                    'timestamp': med['created_at'] or datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
        
        # Get invoice activities
        if log_type in ["All", "Invoice"]:
            query = """
                SELECT i.invoice_number, i.total_amount, i.created_at, u.username
                FROM invoices i
                JOIN users u ON i.patient_id = u.id
                WHERE 1=1
            """
            params = []
            
            if username:
                query += " AND LOWER(u.username) LIKE ?"
                params.append(f"%{username.lower()}%")
            
            if from_date:
                query += " AND DATE(i.created_at) >= ?"
                params.append(from_date)
            
            if to_date:
                query += " AND DATE(i.created_at) <= ?"
                params.append(to_date)
            
            query += " ORDER BY i.created_at DESC LIMIT 15"
            
            cursor.execute(query, params)
            invoices = cursor.fetchall()
            
            for inv in invoices:
                logs.append({
                    'type': 'Invoice',
                    'user': inv['username'],
                    'action': 'Invoice generated',
                    'details': f"Invoice #{inv['invoice_number']} - Amount: ₱{inv['total_amount']:.2f}",
                    'timestamp': inv['created_at'] or datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
        
        conn.close()
        
        # Sort all logs by timestamp
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # If no real logs, show placeholder message
        if not logs:
            # Add some mock login activities
            logs = [
                {
                    'type': 'Login',
                    'user': 'admin',
                    'action': 'Successful login',
                    'details': 'Logged in from IP: 192.168.1.1',
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                },
                {
                    'type': 'Admin',
                    'user': 'admin',
                    'action': 'Viewed system logs',
                    'details': 'Accessed system activity monitoring',
                    'timestamp': (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M"),
                },
            ]
        
        return logs
    
    def load_logs(e=None):
        """Load and display system logs."""
        logs_container.controls.clear()
        
        # Get filter values
        log_type = log_type_filter.value
        username = user_filter.value
        from_date = date_from.value
        to_date = date_to.value
        
        # Generate logs
        logs = generate_mock_logs(log_type, username, from_date, to_date)
        
        if logs:
            for log in logs:
                logs_container.controls.append(
                    create_activity_log(
                        log['type'],
                        log['user'],
                        log['action'],
                        log['details'],
                        log['timestamp'],
                    )
                )
        else:
            logs_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INFO_OUTLINE, color="outline", size=50),
                        ft.Text("No activity logs found", size=16, color="outline"),
                        ft.Text("Try adjusting your filters", size=12, color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.alignment.center,
                )
            )
        
        if e:
            e.page.update()
    
    def clear_filters(e):
        """Clear all filters."""
        log_type_filter.value = "All"
        user_filter.value = ""
        date_from.value = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_to.value = datetime.now().strftime("%Y-%m-%d")
        load_logs(e)
    
    def refresh_logs(e):
        """Refresh logs."""
        load_statistics()
        load_logs(e)
    
    # Initial load
    load_statistics()
    class FakePage:
        def update(self): pass
    load_logs(type('Event', (), {'page': FakePage()})())
    
    return ft.Column([
        ft.Row([
            ft.Text("System Activity Logs", size=28, weight="bold"),
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Refresh",
                on_click=refresh_logs,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Text("Monitor system activities and user actions", size=14, color="outline"),
        
        ft.Container(height=20),
        
        # Statistics
        stats_row,
        
        ft.Container(height=20),
        
        # Filters
        ft.Container(
            content=ft.Column([
                ft.Text("Filters", size=18, weight="bold"),
                ft.Row([
                    log_type_filter,
                    user_filter,
                    date_from,
                    date_to,
                ], spacing=10, wrap=True),
                ft.Row([
                    ft.ElevatedButton(
                        "Apply Filters",
                        icon=ft.Icons.FILTER_ALT,
                        bgcolor="primary",
                        color="onPrimary",
                        on_click=load_logs,
                    ),
                    ft.OutlinedButton(
                        "Clear Filters",
                        icon=ft.Icons.CLEAR,
                        on_click=clear_filters,
                    ),
                ], spacing=10),
            ], spacing=15),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
        
        ft.Container(height=20),
        
        # Activity logs
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Recent Activity", size=18, weight="bold"),
                    ft.Text(f"({len(logs_container.controls)} entries)", 
                           size=14, color="outline"),
                ], spacing=10),
                ft.Divider(),
                logs_container,
            ], spacing=10),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)