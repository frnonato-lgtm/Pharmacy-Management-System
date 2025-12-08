"""Patient detail view for staff (read-only)."""

import flet as ft
from services.database import get_db_connection
from components.navigation_header import NavigationHeader

def StaffPatientDetail(patient_id):
    """Display detailed patient information (read-only)."""
    
    # 1. Fetch Patient Data from DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ? AND role = 'Patient'", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    
    # Handle error if patient not found
    if not row:
        return ft.Column([
            NavigationHeader("Error", show_back=True, back_route="/staff/search"),
            ft.Text("Patient not found", color="error")
        ])
    
    # Convert tuple to dictionary
    patient = {
        'id': row[0], 'full_name': row[4], 'email': row[6],
        'phone': row[7], 'dob': row[8], 'address': row[9],
        'created_at': row[10]
    }
    
    # Helper to create those little info squares
    def info_tile(label, value, icon):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color="secondary", size=20),
                ft.Column([
                    ft.Text(label, size=11, color="outline"),
                    ft.Text(value or "N/A", size=14, weight="bold"),
                ])
            ]),
            padding=15,
            bgcolor="surface",
            border_radius=8,
            border=ft.border.all(1, "outlineVariant"),
            expand=True # Ensures they fill the width evenly
        )
    
    # --- LAYOUT ---
    return ft.Column([
        # Keep back button here so they can return to search
        NavigationHeader(f"Patient: {patient['full_name']}", "View Details (Read-Only)", show_back=True, back_route="/staff/search"),
        
        ft.Container(
            padding=20,
            content=ft.Column([
                # Profile Header Block
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=80, color="primary"),
                        ft.Column([
                            ft.Text(patient['full_name'], size=24, weight="bold"),
                            ft.Text(f"ID: {patient['id']}", size=14, color="outline"),
                            ft.Container(
                                content=ft.Text("Patient", color="white", size=10, weight="bold"),
                                bgcolor="primary", padding=5, border_radius=5
                            )
                        ], spacing=2)
                    ], spacing=20),
                    padding=20,
                    bgcolor="surface",
                    border_radius=12,
                    border=ft.border.all(1, "outlineVariant")
                ),
                
                ft.Container(height=20),
                
                # Contact Info Row
                ft.Text("Contact Info", size=18, weight="bold"),
                ft.Row([
                    info_tile("Email Address", patient['email'], ft.Icons.EMAIL),
                    info_tile("Phone Number", patient['phone'], ft.Icons.PHONE),
                ]),
                
                ft.Container(height=10),
                
                # Personal Info Row
                ft.Text("Personal Details", size=18, weight="bold"),
                ft.Row([
                    info_tile("Date of Birth", patient['dob'], ft.Icons.CAKE),
                    info_tile("Home Address", patient['address'], ft.Icons.HOME),
                ]),
                
                ft.Container(height=30),
                
                # Read-only notice bar at bottom
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOCK, color="white"),
                        ft.Text("You are viewing this record in Read-Only mode.", color="white")
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor="grey",
                    padding=10,
                    border_radius=8
                )
            ])
        )
    ], scroll=ft.ScrollMode.AUTO, spacing=0)