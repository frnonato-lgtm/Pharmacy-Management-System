import flet as ft
from services.database import get_db_connection

def PharmacistDashboard():
    """Overview for Pharmacist."""
    
    conn = get_db_connection()
    pending = conn.execute("SELECT COUNT(*) FROM prescriptions WHERE status = 'Pending'").fetchone()[0]
    conn.close()

    return ft.Column([
        ft.Text("Pharmacist Dashboard", size=28, weight="bold"),
        ft.Container(height=20),
        
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.PENDING_ACTIONS, color="tertiary", size=40),
                ft.Text("Pending Prescriptions", color="outline"),
                ft.Text(str(pending), size=32, weight="bold", color="tertiary")
            ]),
            padding=20, bgcolor="surface", border_radius=10, border=ft.border.all(1, "outlineVariant")
        ),
        
        ft.Container(height=20),
        ft.ElevatedButton("Review Prescriptions", icon=ft.Icons.MEDICAL_SERVICES, on_click=lambda e: e.page.go("/pharmacist/prescriptions"), height=50)
        
    ], scroll=ft.ScrollMode.AUTO)