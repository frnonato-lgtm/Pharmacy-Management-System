"""Patient detail view for staff (read-only)."""

import flet as ft
from services.database import get_db_connection
from components.navigation_header import NavigationHeader

def StaffPatientDetail(patient_id):
    """Display detailed patient information (read-only)."""
    
    # Get patient data
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = ? AND role = 'Patient'", (patient_id,))
    patient_row = cursor.fetchone()
    
    if not patient_row:
        conn.close()
        return ft.Column([
            NavigationHeader("Patient Not Found", show_back=True, back_route="/staff/search"),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=100, color="error"),
                    ft.Text("Patient not found", size=24, weight="bold"),
                    ft.Text(f"Patient ID: {patient_id}", color="outline"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                padding=50,
                expand=True,
            ),
        ])
    
    patient = {
        'id': patient_row[0],
        'username': patient_row[1],
        'full_name': patient_row[4],
        'last_name': patient_row[5],
        'email': patient_row[6],
        'phone': patient_row[7],
        'dob': patient_row[8],
        'address': patient_row[9],
        'created_at': patient_row[10] if len(patient_row) > 10 else None,
    }
    
    # Get prescription count
    cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE patient_id = ?", (patient_id,))
    prescription_count = cursor.fetchone()[0]
    
    # Get order count
    cursor.execute("SELECT COUNT(*) FROM orders WHERE patient_id = ?", (patient_id,))
    order_count = cursor.fetchone()[0]
    
    conn.close()
    
    # Helper: Info card
    def info_card(title, value, icon):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color="primary", size=24),
                    ft.Text(title, size=12, color="outline", weight="bold"),
                ], spacing=10),
                ft.Container(height=5),
                ft.Text(str(value or "Not provided"), size=15, weight="bold"),
            ], spacing=5),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
            bgcolor="surface",
            expand=True,
        )
    
    return ft.Column([
        NavigationHeader(
            f"Patient: {patient['full_name']}",
            "Read-only patient record view",
            show_back=True,
            back_route="/staff/search"
        ),
        
        ft.Container(
            content=ft.Column([
                # Patient header
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            width=80,
                            height=80,
                            bgcolor="primaryContainer",
                            border_radius=40,
                            content=ft.Icon(ft.Icons.PERSON, size=40, color="onPrimaryContainer"),
                            alignment=ft.alignment.center,
                        ),
                        ft.Column([
                            ft.Text(patient['full_name'], size=24, weight="bold"),
                            ft.Text(f"Patient ID: {patient['id']}", size=14, color="outline"),
                            ft.Text(f"Username: {patient['username']}", size=13, color="outline"),
                        ], spacing=3),
                    ], spacing=20),
                    padding=20,
                    bgcolor="surface",
                    border_radius=10,
                    border=ft.border.all(1, "outlineVariant"),
                ),
                
                ft.Container(height=20),
                
                # Statistics
                ft.Row([
                    info_card("Prescriptions", prescription_count, ft.Icons.MEDICATION),
                    info_card("Orders", order_count, ft.Icons.SHOPPING_BAG),
                    info_card("Member Since", patient['created_at'][:10] if patient['created_at'] else "N/A", 
                             ft.Icons.CALENDAR_TODAY),
                ], spacing=15),
                
                ft.Container(height=20),
                
                # Contact Information
                ft.Text("Contact Information", size=20, weight="bold"),
                ft.Row([
                    info_card("Email", patient['email'], ft.Icons.EMAIL),
                    info_card("Phone", patient['phone'], ft.Icons.PHONE),
                ], spacing=15),
                
                ft.Container(height=20),
                
                # Personal Information
                ft.Text("Personal Information", size=20, weight="bold"),
                ft.Row([
                    info_card("Date of Birth", patient['dob'], ft.Icons.CAKE),
                    info_card("Address", patient['address'], ft.Icons.HOME),
                ], spacing=15),
                
                ft.Container(height=20),
                
                # Read-only notice
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOCK, color="tertiary", size=24),
                        ft.Column([
                            ft.Text("Read-Only Access", size=14, weight="bold", color="tertiary"),
                            ft.Text(
                                "You can view patient information but cannot make changes. Contact administrators for updates.",
                                size=12,
                                color="outline",
                            ),
                        ], spacing=3, expand=True),
                    ], spacing=15),
                    bgcolor=ft.Colors.with_opacity(0.05, "tertiary"),
                    padding=15,
                    border_radius=8,
                    border=ft.border.all(1, "tertiary"),
                ),
            ], spacing=0),
            padding=20,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)