import flet as ft
from services.database import get_db_connection

def InvoicesView():
    """Create new invoices."""
    
    def create_invoice(e):
        # Just a visual confirmation for now
        e.page.snack_bar = ft.SnackBar(ft.Text("Invoice Generated Successfully!"))
        e.page.snack_bar.open = True
        e.page.update()

    patient_dropdown = ft.Dropdown(label="Select Patient", width=400)
    
    # Load patients
    conn = get_db_connection()
    patients = conn.execute("SELECT id, full_name FROM users WHERE role='Patient'").fetchall()
    conn.close()
    
    for p in patients:
        patient_dropdown.options.append(ft.dropdown.Option(text=p['full_name'], key=str(p['id'])))

    return ft.Column([
        ft.Text("Generate Invoice", size=28, weight="bold"),
        ft.Container(height=20),
        
        ft.Container(
            padding=20, border=ft.border.all(1, "outlineVariant"), border_radius=10,
            content=ft.Column([
                ft.Text("New Transaction", weight="bold"),
                patient_dropdown,
                ft.TextField(label="Amount (P)", keyboard_type="number", width=400),
                ft.TextField(label="Notes", multiline=True, width=400),
                ft.ElevatedButton("Create Invoice", icon=ft.Icons.ADD, on_click=create_invoice, bgcolor="primary", color="onPrimary")
            ])
        )
    ], scroll=ft.ScrollMode.AUTO)