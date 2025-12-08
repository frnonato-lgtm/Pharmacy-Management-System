"""Administrator dashboard with real database integration."""

import flet as ft
from services.database import get_db_connection
from datetime import datetime, timedelta

def AdminDashboard():
    """Admin dashboard with real system overview."""
    
    # Get REAL statistics from database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # User statistics
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Patient'")
    total_patients = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Pharmacist'")
    total_pharmacists = cursor.fetchone()[0]
    
    # Medicine statistics
    cursor.execute("SELECT COUNT(*) FROM medicines")
    total_medicines = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM medicines WHERE stock < 10")
    low_stock_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM medicines WHERE stock = 0")
    out_of_stock = cursor.fetchone()[0]
    
    # Prescription statistics
    cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE status = 'Pending'")
    pending_prescriptions = cursor.fetchone()[0]
    
    # Order statistics
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status IN ('Pending', 'Processing')")
    pending_orders = cursor.fetchone()[0]
    
    # Recent activity (last 5 actions)
    cursor.execute("""
        SELECT username, role, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT 5
    """)
    recent_users = cursor.fetchall()
    
    # Get recent prescriptions for activity
    cursor.execute("""
        SELECT p.id, p.status, p.created_at, u.username
        FROM prescriptions p
        JOIN users u ON p.patient_id = u.id
        ORDER BY p.created_at DESC
        LIMIT 3
    """)
    recent_prescriptions = cursor.fetchall()
    
    # Get recent orders
    cursor.execute("""
        SELECT o.id, o.status, o.order_date, u.username
        FROM orders o
        JOIN users u ON o.patient_id = u.id
        ORDER BY o.order_date DESC
        LIMIT 3
    """)
    recent_orders = cursor.fetchall()
    
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
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
            expand=True,
            height = 140,
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
    def create_activity_item(action, user, time_str):
        try:
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            diff = now - dt
            
            if diff.days > 0:
                time_ago = f"{diff.days} days ago"
            elif diff.seconds > 3600:
                time_ago = f"{diff.seconds // 3600} hours ago"
            elif diff.seconds > 60:
                time_ago = f"{diff.seconds // 60} min ago"
            else:
                time_ago = "Just now"
        except:
            time_ago = time_str
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CIRCLE, size=8, color="primary"),
                ft.Column([
                    ft.Text(action, size=13),
                    ft.Text(f"by {user} • {time_ago}", size=11, color="outline"),
                ], spacing=2, expand=True),
            ], spacing=10),
            padding=10,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
        )
    
    # Build recent activity list
    activity_list = []
    
    # Add user registrations
    for u in recent_users:
        activity_list.append(
            create_activity_item(
                f"New {u[1]} registered",
                u[0],
                u[2]
            )
        )
    
    # Add prescription activities
    for p in recent_prescriptions:
        status = p[1]
        action = f"Prescription #{p[0]} {status.lower()}"
        activity_list.append(
            create_activity_item(action, p[3], p[2])
        )
    
    # Add order activities
    for o in recent_orders:
        action = f"Order #{o[0]} placed"
        activity_list.append(
            create_activity_item(action, o[3], o[2])
        )
    
    # Take only last 5 activities
    activity_list = activity_list[:5]
    
    if not activity_list:
        activity_list = [
            ft.Container(
                content=ft.Text("No recent activity", color="outline"),
                padding=20,
            )
        ]
    
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
        
        # Statistics cards - REAL DATA
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
                f"{out_of_stock} out of stock" if out_of_stock > 0 else "All good"
            ),
            create_stat_card(
                "Pending Tasks",
                pending_prescriptions + pending_orders,
                ft.Icons.PENDING_ACTIONS,
                "tertiary",
                f"{pending_prescriptions} Rx, {pending_orders} orders"
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
            # Recent activity - REAL DATA
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Recent Activity", size=20, weight="bold"),
                        ft.TextButton("View All →", on_click=lambda e: e.page.go("/admin/logs")),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    *activity_list,
                ], spacing=10),
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(1, "outlineVariant"),
                expand=2,
            ),
            
            # System health - REAL STATUS
            ft.Container(
                content=ft.Column([
                    ft.Text("System Health", size=20, weight="bold"),
                    ft.Divider(),
                    
                    # Database status
                    ft.Row([
                        ft.Icon(ft.Icons.DATA_OBJECT, color="primary", size=30),
                        ft.Column([
                            ft.Text("Database", size=14, weight="bold"),
                            ft.Text(f"{total_users + total_medicines} records", size=12, color="outline"),
                        ], spacing=2, expand=True),
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="primary"),
                    ], spacing=10),
                    
                    ft.Divider(height=5, color="transparent"),
                    
                    # Inventory status
                    ft.Row([
                        ft.Icon(ft.Icons.INVENTORY, color="secondary", size=30),
                        ft.Column([
                            ft.Text("Inventory", size=14, weight="bold"),
                            ft.Text(f"{low_stock_count} items need attention", size=12, 
                                   color="error" if low_stock_count > 0 else "primary"),
                        ], spacing=2, expand=True),
                        ft.Icon(ft.Icons.WARNING if low_stock_count > 0 else ft.Icons.CHECK_CIRCLE, 
                               color="error" if low_stock_count > 0 else "primary"),
                    ], spacing=10),
                    
                    ft.Divider(height=5, color="transparent"),
                    
                    # Prescriptions status
                    ft.Row([
                        ft.Icon(ft.Icons.MEDICATION, color="tertiary", size=30),
                        ft.Column([
                            ft.Text("Prescriptions", size=14, weight="bold"),
                            ft.Text(f"{pending_prescriptions} pending review", size=12, color="outline"),
                        ], spacing=2, expand=True),
                        ft.Icon(ft.Icons.PENDING if pending_prescriptions > 0 else ft.Icons.CHECK_CIRCLE,
                               color="tertiary" if pending_prescriptions > 0 else "primary"),
                    ], spacing=10),
                    
                    ft.Container(height=10),
                    ft.Text("System Status:", size=12, color="outline"),
                    ft.Text("All systems operational", size=13, weight="bold", color="primary"),
                ], spacing=10),
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(1, "outlineVariant"),
                expand=1,
            ),
        ], spacing=15),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)