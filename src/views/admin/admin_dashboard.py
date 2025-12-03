"""Administrator dashboard overview."""

import flet as ft
from services.database import get_db_connection

def AdminDashboard():
    """Admin dashboard with system overview."""
    
    # Get statistics from database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Patient'")
    total_patients = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM medicines")
    total_medicines = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM medicines WHERE stock < 10")
    low_stock_count = cursor.fetchone()[0]
    
    conn.close()
    
    # Stat card helper
    def create_stat_card(title, value, icon, color, subtitle=""):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=40),
                    ft.Column([
                        ft.Text(title, size=14, color="outline"),
                        ft.Text(
                            str(value),
                            size=32,
                            weight="bold",
                            color=color,
                        ),
                        ft.Text(subtitle, size=11, color="outline") if subtitle else ft.Container(),
                    ], spacing=2, expand=True),
                ], spacing=15),
            ]),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
            expand=True,
        )
    
    # Quick action button
    def create_action_button(text, icon, route, color):
        return ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(icon, color="onPrimary"),
                ft.Text(text, color="onPrimary"),
            ], spacing=10),
            bgcolor=color,
            on_click=lambda e: e.page.go(route),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=15,
            ),
        )
    
    # Recent activity item
    def create_activity_item(user, action, time):
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CIRCLE, size=8, color="primary"),
                ft.Column([
                    ft.Text(f"{user} {action}", size=13),
                    ft.Text(time, size=11, color="outline"),
                ], spacing=2, expand=True),
            ], spacing=10),
            padding=10,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
        )
    
    return ft.Column([
        # Welcome header
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, color="primary", size=40),
                ft.Column([
                    ft.Text(
                        "System Administration",
                        size=28,
                        weight="bold",
                    ),
                    ft.Text(
                        "Monitor and manage the pharmacy system",
                        size=14,
                        color="outline",
                    ),
                ], spacing=5),
            ], spacing=15),
            padding=20,
        ),
        
        # Statistics cards
        ft.Row([
            create_stat_card(
                "Total Users",
                total_users,
                ft.Icons.PEOPLE,
                "primary",
                f"{total_patients} patients"
            ),
            create_stat_card(
                "Total Medicines",
                total_medicines,
                ft.Icons.MEDICATION,
                "secondary",
            ),
            create_stat_card(
                "Low Stock Items",
                low_stock_count,
                ft.Icons.WARNING,
                "error" if low_stock_count > 0 else "primary",
                "Needs attention" if low_stock_count > 0 else "All good"
            ),
            create_stat_card(
                "System Status",
                "Active",
                ft.Icons.CHECK_CIRCLE,
                "primary",
                "All systems operational"
            ),
        ], spacing=15),
        
        ft.Container(height=20),
        
        # Quick actions
        ft.Container(
            content=ft.Column([
                ft.Text("Quick Actions", size=20, weight="bold"),
                ft.Row([
                    create_action_button(
                        "Manage Users",
                        ft.Icons.PEOPLE,
                        "/admin/users",
                        "primary",
                    ),
                    create_action_button(
                        "View Reports",
                        ft.Icons.ANALYTICS,
                        "/admin/reports",
                        "secondary",
                    ),
                    create_action_button(
                        "System Logs",
                        ft.Icons.HISTORY,
                        "/admin/logs",
                        "tertiary",
                    ),
                ], spacing=15, wrap=True),
            ], spacing=15),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
        
        ft.Container(height=20),
        
        # Recent activity and system health
        ft.Row([
            # Recent activity
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Recent Activity", size=20, weight="bold"),
                        ft.TextButton("View All →", on_click=lambda e: e.page.go("/admin/logs")),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    create_activity_item("John Doe", "registered as new patient", "5 min ago"),
                    create_activity_item("Dr. Chen", "approved prescription #1234", "15 min ago"),
                    create_activity_item("Admin", "updated stock for Paracetamol", "1 hour ago"),
                    create_activity_item("Billing Clerk", "processed invoice #5001", "2 hours ago"),
                ], spacing=10),
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(1, "outlineVariant"),
                expand=2,
            ),
            
            # System health
            ft.Container(
                content=ft.Column([
                    ft.Text("System Health", size=20, weight="bold"),
                    ft.Divider(),
                    ft.Row([
                        ft.Icon(ft.Icons.DATA_OBJECT, color="primary", size=30),
                        ft.Column([
                            ft.Text("Database", size=14, weight="bold"),
                            ft.Text("Connected", size=12, color="primary"),
                        ], spacing=2, expand=True),
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="primary"),
                    ], spacing=10),
                    
                    ft.Divider(height=5, color="transparent"),
                    
                    ft.Row([
                        ft.Icon(ft.Icons.STORAGE, color="primary", size=30),
                        ft.Column([
                            ft.Text("Storage", size=14, weight="bold"),
                            ft.Text("45% Used", size=12, color="outline"),
                        ], spacing=2, expand=True),
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="primary"),
                    ], spacing=10),
                    
                    ft.Divider(height=5, color="transparent"),
                    
                    ft.Row([
                        ft.Icon(ft.Icons.SECURITY, color="primary", size=30),
                        ft.Column([
                            ft.Text("Security", size=14, weight="bold"),
                            ft.Text("No Issues", size=12, color="primary"),
                        ], spacing=2, expand=True),
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="primary"),
                    ], spacing=10),
                    
                    ft.Container(height=10),
                    ft.Text("Last Backup:", size=12, color="outline"),
                    ft.Text("Nov 26, 2025 - 02:00 AM", size=13, weight="bold"),
                ], spacing=10),
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(1, "outlineVariant"),
                expand=1,
            ),
        ], spacing=15),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)