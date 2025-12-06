"""Staff dashboard with quick access and statistics."""

import flet as ft
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader

def StaffDashboard():
    """Staff member dashboard with overview."""
    
    user = AppState.get_user()
    user_name = user['full_name'] if user else "Staff Member"
    
    # Get statistics
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count total patients
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Patient'")
    total_patients = cursor.fetchone()[0]
    
    # Count patients registered today
    cursor.execute("""
        SELECT COUNT(*) FROM users 
        WHERE role = 'Patient' AND DATE(created_at) = DATE('now')
    """)
    new_today = cursor.fetchone()[0]
    
    # Count active prescriptions
    cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE status = 'Pending'")
    active_prescriptions = cursor.fetchone()[0]
    
    # Get recent patient registrations
    cursor.execute("""
        SELECT id, full_name, phone, email, created_at
        FROM users
        WHERE role = 'Patient'
        ORDER BY created_at DESC
        LIMIT 5
    """)
    recent_patients = cursor.fetchall()
    
    conn.close()
    
    # Helper: Create stat card
    def create_stat_card(title, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=40),
                ft.Text(str(value), size=32, weight="bold", color=color),
                ft.Text(title, size=12, color="outline", text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
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
    
    # Helper: Create recent patient item
    def create_patient_item(patient):
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.PERSON, color="primary", size=24),
                ft.Column([
                    ft.Text(patient[1], size=14, weight="bold"),
                    ft.Text(f"Phone: {patient[2]}", size=12, color="outline"),
                    ft.Text(f"Registered: {patient[4][:10]}", size=11, color="outline", italic=True),
                ], spacing=2, expand=True),
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD,
                    icon_color="primary",
                    tooltip="View Details",
                    on_click=lambda e, pid=patient[0]: view_patient_details(e, pid),
                ),
            ], spacing=10),
            padding=12,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
            bgcolor="surface",
        )
    
    def view_patient_details(e, patient_id):
        """Navigate to patient details."""
        e.page.go(f"/staff/patient/{patient_id}")
    
    return ft.Column([
        # Header
        NavigationHeader(
            f"Welcome, {user_name}",
            "Staff Portal - Assist with patient records and inquiries",
            show_back=False,
            show_forward=False,
        ),
        
        # Statistics
        ft.Row([
            create_stat_card("Total Patients", total_patients, ft.Icons.PEOPLE, "primary"),
            create_stat_card("Registered Today", new_today, ft.Icons.PERSON_ADD, "secondary"),
            create_stat_card("Active Prescriptions", active_prescriptions, ft.Icons.MEDICATION, "tertiary"),
        ], spacing=15),
        
        ft.Container(height=20),
        
        # Quick actions
        ft.Container(
            content=ft.Column([
                ft.Text("Quick Actions", size=20, weight="bold"),
                ft.Row([
                    create_action_button(
                        "Search Patients",
                        ft.Icons.SEARCH,
                        "/staff/search",
                        "primary",
                    ),
                    create_action_button(
                        "View All Patients",
                        ft.Icons.LIST,
                        "/staff/patients",
                        "secondary",
                    ),
                    create_action_button(
                        "Help Desk",
                        ft.Icons.HELP,
                        "/staff/help",
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
        
        # Main content
        ft.Row([
            # Recent patients
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.HISTORY, color="primary", size=24),
                        ft.Text("Recent Patient Registrations", size=20, weight="bold"),
                    ], spacing=10),
                    ft.Divider(),
                    
                    *([create_patient_item(patient) for patient in recent_patients] if recent_patients else [
                        ft.Container(
                            content=ft.Text("No recent registrations", size=14, color="outline", italic=True),
                            padding=30,
                            alignment=ft.alignment.center,
                        )
                    ]),
                    
                    ft.Container(height=10),
                    ft.TextButton(
                        "View All Patients →",
                        on_click=lambda e: e.page.go("/staff/patients"),
                    ),
                ], spacing=10),
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(1, "outlineVariant"),
                expand=2,
            ),
            
            # Staff info and guidelines
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.INFO, color="secondary", size=24),
                        ft.Text("Staff Guidelines", size=20, weight="bold"),
                    ], spacing=10),
                    ft.Divider(),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Your Responsibilities:", size=14, weight="bold"),
                            ft.Text("• Assist patients with inquiries", size=12),
                            ft.Text("• Search and verify patient records", size=12),
                            ft.Text("• Help with data entry and updates", size=12),
                            ft.Text("• Support pharmacists and staff", size=12),
                        ], spacing=8),
                        bgcolor=ft.Colors.with_opacity(0.05, "primary"),
                        padding=15,
                        border_radius=8,
                        border=ft.border.all(1, "primary"),
                    ),
                    
                    ft.Container(height=15),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.LOCK, color="tertiary", size=20),
                                ft.Text("Read-Only Access", size=13, weight="bold", color="tertiary"),
                            ], spacing=8),
                            ft.Text(
                                "You have view-only access to patient records. Contact administrators for data modifications.",
                                size=11,
                                color="outline",
                            ),
                        ], spacing=8),
                        bgcolor=ft.Colors.with_opacity(0.05, "tertiary"),
                        padding=12,
                        border_radius=8,
                    ),
                    
                    ft.Container(height=15),
                    
                    ft.Text("Quick Tips:", size=14, weight="bold"),
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.TIPS_AND_UPDATES, size=16, color="secondary"),
                            ft.Text("Use patient name or phone to search", size=12),
                        ], spacing=5),
                        ft.Row([
                            ft.Icon(ft.Icons.TIPS_AND_UPDATES, size=16, color="secondary"),
                            ft.Text("Verify patient ID before sharing info", size=12),
                        ], spacing=5),
                        ft.Row([
                            ft.Icon(ft.Icons.TIPS_AND_UPDATES, size=16, color="secondary"),
                            ft.Text("Report issues to administrators", size=12),
                        ], spacing=5),
                    ], spacing=8),
                ], spacing=10),
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(1, "outlineVariant"),
                expand=1,
            ),
        ], spacing=15, vertical_alignment=ft.CrossAxisAlignment.START),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)