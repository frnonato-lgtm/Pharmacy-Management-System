import flet as ft
from services.database import get_db_connection

def BillingDashboard():
    """Financial stats."""
    
    conn = get_db_connection()
    # Calculate totals from paid invoices
    total_sales = conn.execute("SELECT SUM(total_amount) FROM invoices WHERE status='Paid'").fetchone()[0] or 0
    conn.close()

    return ft.Column([
        ft.Text("Financial Overview", size=28, weight="bold"),
        ft.Container(height=20),
        
        ft.Container(
            padding=20, bgcolor="primaryContainer", border_radius=10, 
            content=ft.Column([
                ft.Icon(ft.Icons.ATTACH_MONEY, color="onPrimaryContainer", size=30),
                ft.Text("Total Sales", color="onPrimaryContainer"),
                ft.Text(f"P {total_sales:,.2f}", size=28, weight="bold", color="onPrimaryContainer")
            ]) 
        ),

        ft.Container(height=20),
        ft.Text("Actions", size=20, weight="bold"),
        ft.ElevatedButton("Generate Invoice", icon=ft.Icons.RECEIPT, on_click=lambda e: e.page.go("/billing/invoices"), height=50)
    ], scroll=ft.ScrollMode.AUTO)