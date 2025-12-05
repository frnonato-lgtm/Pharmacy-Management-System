"""Pharmacist dashboard overview."""

import flet as ft
from services.database import get_db_connection
from state.app_state import AppState
#from components.navigation_header import NavigationHeader

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
    cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE status = 'Approved'")
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
    
    # Helper: Create prescription item
    def create_prescription_item(rx_id, patient_name, medicine, status, status_color, time):
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(f"Prescription #{rx_id}", weight="bold", size=14),
                    ft.Text(f"Patient: {patient_name}", size=12, color="outline"),
                    ft.Text(f"Medicine: {medicine}", size=12),
                    ft.Text(f"Submitted: {time}", size=11, color="outline", italic=True),
                ], spacing=3, expand=True),
                ft.Container(
                    content=ft.Text(status, size=12, weight="bold", color="onPrimaryContainer"),
                    bgcolor=ft.Colors.with_opacity(0.2, status_color),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border_radius=15,
                ),
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD,
                    icon_color="primary",
                    tooltip="Review Prescription",
                    on_click=lambda e: e.page.go(f"/pharmacist/prescription/{rx_id}"),
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
    
    return ft.Column([
        # Welcome header
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.MEDICAL_SERVICES, color="primary", size=40),
                ft.Column([
                    ft.Text(
                        f"Welcome, {user_name}",
                        size=28,
                        weight="bold",
                    ),
                    ft.Text(
                        "Pharmacist Dashboard - Review and validate prescriptions",
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
                "Pending Reviews",
                pending_rx if pending_rx > 0 else 8,  # Mock data fallback
                ft.Icons.PENDING_ACTIONS,
                "tertiary",
                "Requires action"
            ),
            create_stat_card(
                "Approved Today",
                approved_rx if approved_rx > 0 else 16,  # Mock data
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
                    
                    # Sample pending prescriptions (replace with real DB data)
                    create_prescription_item(
                        "1234",
                        "John Doe",
                        "Amoxicillin 500mg",
                        "Pending",
                        "tertiary",
                        "2 hours ago"
                    ),
                    create_prescription_item(
                        "1235",
                        "Jane Smith",
                        "Paracetamol 500mg",
                        "Pending",
                        "tertiary",
                        "3 hours ago"
                    ),
                    create_prescription_item(
                        "1236",
                        "Robert Johnson",
                        "Ibuprofen 400mg",
                        "Pending",
                        "tertiary",
                        "5 hours ago"
                    ),
                    
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
                    
                    create_alert_item(
                        "3 medicines are low in stock",
                        ft.Icons.WARNING,
                        "error"
                    ),
                    
                    create_alert_item(
                        "2 prescriptions expiring today",
                        ft.Icons.SCHEDULE,
                        "tertiary"
                    ),
                    
                    create_alert_item(
                        "System maintenance tonight at 11 PM",
                        ft.Icons.INFO,
                        "secondary"
                    ),
                    
                    ft.Container(height=10),
                    
                    ft.Text("Recent Activity", size=16, weight="bold"),
                    ft.Divider(height=10),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Text("✓ Approved Prescription #1230", size=12),
                            ft.Text("✓ Dispensed Amoxicillin to John Doe", size=12),
                            ft.Text("✓ Updated patient notes", size=12),
                        ], spacing=8),
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