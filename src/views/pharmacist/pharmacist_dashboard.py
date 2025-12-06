"""Pharmacist dashboard overview with real database integration."""

import flet as ft
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader
from datetime import datetime

def PharmacistDashboard():
    """Main pharmacist dashboard with statistics and quick actions."""
    
    user = AppState.get_user()
    user_name = user['full_name'] if user else "Pharmacist"
    
    # Get statistics from database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count pending prescriptions
    cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE status = 'Pending'")
    result = cursor.fetchone()
    pending_rx = result[0] if result else 0
    
    # Count approved prescriptions today
    cursor.execute("""
        SELECT COUNT(*) FROM prescriptions 
        WHERE status = 'Approved' 
        AND DATE(reviewed_date) = DATE('now')
    """)
    result = cursor.fetchone()
    approved_rx = result[0] if result else 0
    
    # Count total patients
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Patient'")
    result = cursor.fetchone()
    total_patients = result[0] if result else 0
    
    # Count medicines in stock
    cursor.execute("SELECT COUNT(*) FROM medicines WHERE stock > 0")
    result = cursor.fetchone()
    medicines_available = result[0] if result else 0
    
    # Get pending prescriptions with patient info
    cursor.execute("""
        SELECT p.id, p.created_at, p.status,
               u.full_name as patient_name,
               m.name as medicine_name
        FROM prescriptions p
        LEFT JOIN users u ON p.patient_id = u.id
        LEFT JOIN medicines m ON p.medicine_id = m.id
        WHERE p.status = 'Pending'
        ORDER BY p.created_at DESC
        LIMIT 5
    """)
    pending_prescriptions = cursor.fetchall()
    
    # Get recent activity from activity_log
    cursor.execute("""
        SELECT action, details, timestamp
        FROM activity_log
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 5
    """, (user['id'],))
    recent_activities = cursor.fetchall()
    
    # Get low stock alerts
    cursor.execute("""
        SELECT name, stock
        FROM medicines
        WHERE stock < 10 AND stock > 0
        ORDER BY stock ASC
        LIMIT 3
    """)
    low_stock_medicines = cursor.fetchall()
    
    conn.close()
    
    # Helper: Create stat card
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
    
    # Helper: Create quick action button
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
    
    # Helper: Format time ago
    def time_ago(timestamp_str):
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            delta = now - timestamp
            
            if delta.days > 0:
                return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
            elif delta.seconds >= 3600:
                hours = delta.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif delta.seconds >= 60:
                minutes = delta.seconds // 60
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                return "Just now"
        except:
            return timestamp_str
    
    # Helper: Create prescription item
    def create_prescription_item(rx):
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(f"Prescription #{rx[0]}", weight="bold", size=14),
                    ft.Text(f"Patient: {rx[3]}", size=12, color="outline"),
                    ft.Text(f"Medicine: {rx[4]}", size=12),
                    ft.Text(f"Submitted: {time_ago(rx[1])}", size=11, color="outline", italic=True),
                ], spacing=3, expand=True),
                ft.Container(
                    content=ft.Text("Pending", size=12, weight="bold", color="onTertiaryContainer"),
                    bgcolor=ft.Colors.with_opacity(0.2, "tertiary"),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border_radius=15,
                ),
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD,
                    icon_color="primary",
                    tooltip="Review Prescription",
                    on_click=lambda e, rx_id=rx[0]: e.page.go(f"/pharmacist/prescription/{rx_id}"),
                ),
            ], spacing=10),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
            bgcolor="surface",
        )
    
    # Helper: Create alert item
    def create_alert_item(message, icon, color):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=color, size=24),
                ft.Text(message, size=13, expand=True),
            ], spacing=10),
            padding=12,
            border=ft.border.all(1, color),
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.05, color),
        )
    
    # Helper: Create activity item
    def create_activity_item(action, details, timestamp):
        action_icons = {
            'prescription_approved': '✓',
            'prescription_rejected': '✗',
            'prescription_dispensed': '📦',
            'medicine_updated': '💊',
        }
        icon = action_icons.get(action, '•')
        
        return ft.Text(
            f"{icon} {details}",
            size=12,
            color="outline",
        )
    
    # Build pending prescriptions list
    pending_rx_widgets = []
    if pending_prescriptions:
        for rx in pending_prescriptions:
            pending_rx_widgets.append(create_prescription_item(rx))
    else:
        pending_rx_widgets.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=60, color="primary"),
                    ft.Text("No pending prescriptions!", size=16, color="outline"),
                    ft.Text("Great job! All prescriptions have been reviewed.", size=12, color="outline"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=30,
            )
        )
    
    # Build recent activity list
    activity_widgets = []
    if recent_activities:
        for activity in recent_activities:
            activity_widgets.append(create_activity_item(activity[0], activity[1], activity[2]))
    else:
        activity_widgets.append(
            ft.Text("No recent activity", size=12, color="outline", italic=True)
        )
    
    # Build alerts
    alert_widgets = []
    
    # Low stock alerts
    if low_stock_medicines:
        alert_widgets.append(
            create_alert_item(
                f"{len(low_stock_medicines)} medicine(s) are low in stock",
                ft.Icons.WARNING,
                "error"
            )
        )
    
    # Pending prescriptions alert
    if pending_rx > 5:
        alert_widgets.append(
            create_alert_item(
                f"{pending_rx} prescriptions need review",
                ft.Icons.PRIORITY_HIGH,
                "tertiary"
            )
        )
    
    # If no alerts
    if not alert_widgets:
        alert_widgets.append(
            create_alert_item(
                "All systems normal",
                ft.Icons.CHECK_CIRCLE,
                "primary"
            )
        )
    
    return ft.Column([
        # Navigation header (no back button on dashboard - it's the home page)
        NavigationHeader(
            f"Welcome, {user_name}",
            "Pharmacist Dashboard - Review and validate prescriptions",
            show_back=False,  # Dashboard is the starting point
            show_forward=False,
        ),
        
        # Statistics cards
        ft.Row([
            create_stat_card(
                "Pending Reviews",
                pending_rx,
                ft.Icons.PENDING_ACTIONS,
                "tertiary",
                "Requires action"
            ),
            create_stat_card(
                "Approved Today",
                approved_rx,
                ft.Icons.CHECK_CIRCLE,
                "primary",
                "This shift"
            ),
            create_stat_card(
                "Total Patients",
                total_patients,
                ft.Icons.PEOPLE,
                "secondary",
            ),
            create_stat_card(
                "Medicines Available",
                medicines_available,
                ft.Icons.MEDICATION,
                "primary",
            ),
        ], spacing=15),
        
        ft.Container(height=20),
        
        # Quick actions
        ft.Container(
            content=ft.Column([
                ft.Text("Quick Actions", size=20, weight="bold"),
                ft.Row([
                    create_action_button(
                        "Review Prescriptions",
                        ft.Icons.ASSIGNMENT,
                        "/pharmacist/prescriptions",
                        "primary",
                    ),
                    create_action_button(
                        "Search Medicines",
                        ft.Icons.SEARCH,
                        "/pharmacist/medicines",
                        "secondary",
                    ),
                    create_action_button(
                        "Generate Report",
                        ft.Icons.ANALYTICS,
                        "/pharmacist/reports",
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
        
        # Main content area
        ft.Row([
            # Pending prescriptions
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.PRIORITY_HIGH, color="tertiary", size=24),
                        ft.Text("Prescriptions Requiring Review", size=20, weight="bold"),
                    ], spacing=10),
                    ft.Divider(),
                    
                    *pending_rx_widgets,
                    
                    ft.Container(height=10),
                    ft.TextButton(
                        "View All Prescriptions →",
                        on_click=lambda e: e.page.go("/pharmacist/prescriptions"),
                    ),
                ], spacing=10),
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(1, "outlineVariant"),
                expand=2,
            ),
            
            # Alerts and notifications
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color="error", size=24),
                        ft.Text("Alerts & Notifications", size=20, weight="bold"),
                    ], spacing=10),
                    ft.Divider(),
                    
                    *alert_widgets,
                    
                    ft.Container(height=15),
                    
                    ft.Text("Recent Activity", size=16, weight="bold"),
                    ft.Divider(height=10),
                    
                    ft.Container(
                        content=ft.Column(
                            activity_widgets,
                            spacing=8,
                        ),
                        padding=10,
                        border=ft.border.all(1, "outlineVariant"),
                        border_radius=8,
                    ),
                ], spacing=10),
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(1, "outlineVariant"),
                expand=1,
            ),
        ], spacing=15, vertical_alignment=ft.CrossAxisAlignment.START),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)