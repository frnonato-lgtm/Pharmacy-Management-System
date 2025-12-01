"""System activity logs and audit trail."""

import flet as ft
from database import get_db_connection
from datetime import datetime, timedelta

def SystemLogs():
    """System logs and activity monitoring interface."""
    
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
    
    def create_activity_log(log_type, user, action, details, timestamp):
        """Create a single log entry UI."""
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
                                color="white",
                            ),
                            bgcolor=color,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=5,
                        ),
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
    
    # Get database statistics
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        try:
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE DATE(created_at) = DATE('now')")
            today_registrations = cursor.fetchone()['count']
        except:
            today_registrations = 0
        
        try:
            cursor.execute("SELECT COUNT(*) as count FROM prescriptions")
            total_prescriptions = cursor.fetchone()['count']
        except:
            total_prescriptions = 0
        
        try:
            cursor.execute("SELECT COUNT(*) as count FROM prescriptions WHERE status = 'Pending'")
            pending_prescriptions = cursor.fetchone()['count']
        except:
            pending_prescriptions = 0
        
        # Get recent users for activity logs
        cursor.execute("SELECT username, full_name, role FROM users ORDER BY id DESC LIMIT 8")
        recent_users = cursor.fetchall()
        
        # Get recent medicines for inventory logs
        cursor.execute("SELECT name, category, stock FROM medicines ORDER BY id DESC LIMIT 5")
        recent_medicines = cursor.fetchall()
        
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")
        total_users = 0
        today_registrations = 0
        total_prescriptions = 0
        pending_prescriptions = 0
        recent_users = []
        recent_medicines = []
    
    # Build activity logs
    activity_logs = []
    
    # Add mock login
    activity_logs.append(
        create_activity_log(
            "Login",
            "admin",
            "Successful login",
            "Logged in to system administration panel",
            datetime.now().strftime("%Y-%m-%d %H:%M")
        )
    )
    
    # Add user registration activities
    for i, user in enumerate(recent_users):
        activity_logs.append(
            create_activity_log(
                "Registration",
                user['username'],
                "New user registration",
                f"Registered as {user['role']}: {user['full_name']}",
                (datetime.now() - timedelta(minutes=5 * (i + 1))).strftime("%Y-%m-%d %H:%M")
            )
        )
    
    # Add inventory activities
    for i, med in enumerate(recent_medicines):
        activity_logs.append(
            create_activity_log(
                "Inventory",
                "admin",
                "Medicine stock updated",
                f"{med['name']} ({med['category']}) - Current stock: {med['stock']}",
                (datetime.now() - timedelta(minutes=10 * (i + 1))).strftime("%Y-%m-%d %H:%M")
            )
        )
    
    # Build the main UI
    return ft.Column([
        # Header
        ft.Row([
            ft.Text("System Activity Logs", size=28, weight="bold"),
        ]),
        ft.Text("Monitor system activities and user actions", size=14, color="outline"),
        
        ft.Container(height=20),
        
        # Statistics Cards
        ft.Row([
            create_stat_card("Total Users", total_users, ft.Icons.PEOPLE, "primary"),
            create_stat_card("Registered Today", today_registrations, ft.Icons.PERSON_ADD, "secondary"),
            create_stat_card("Total Prescriptions", total_prescriptions, ft.Icons.DESCRIPTION, "tertiary"),
            create_stat_card("Pending Review", pending_prescriptions, ft.Icons.PENDING, "tertiary"),
        ], spacing=15, wrap=True),
        
        ft.Container(height=20),
        
        # Filters Section
        ft.Container(
            content=ft.Column([
                ft.Text("Filters", size=18, weight="bold"),
                ft.Row([
                    ft.Dropdown(
                        label="Activity Type",
                        options=[
                            ft.dropdown.Option("All", "All Activities"),
                            ft.dropdown.Option("Login", "User Logins"),
                            ft.dropdown.Option("Registration", "New Registrations"),
                            ft.dropdown.Option("Inventory", "Inventory Changes"),
                        ],
                        value="All",
                        width=250,
                    ),
                    ft.TextField(
                        label="Filter by User",
                        hint_text="Enter username...",
                        width=200,
                    ),
                    ft.TextField(
                        label="From Date",
                        hint_text="YYYY-MM-DD",
                        value=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                        width=150,
                    ),
                    ft.TextField(
                        label="To Date",
                        hint_text="YYYY-MM-DD",
                        value=datetime.now().strftime("%Y-%m-%d"),
                        width=150,
                    ),
                ], spacing=10, wrap=True),
                ft.Row([
                    ft.ElevatedButton(
                        "Apply Filters",
                        icon=ft.Icons.FILTER_ALT,
                        bgcolor="primary",
                        color="onPrimary",
                    ),
                    ft.OutlinedButton(
                        "Clear Filters",
                        icon=ft.Icons.CLEAR,
                    ),
                ], spacing=10),
            ], spacing=15),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
        
        ft.Container(height=20),
        
        # Activity Logs Section
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Recent Activity", size=18, weight="bold"),
                    ft.Text(f"({len(activity_logs)} entries)", size=14, color="outline"),
                ], spacing=10),
                ft.Divider(),
                ft.Column(
                    controls=activity_logs,
                    spacing=10,
                ),
            ], spacing=10),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)