import flet as ft
from services.database import get_db_connection

def PrescriptionsView():
    """List of prescriptions to review."""
    
    rx_list = ft.Column(spacing=10)

    def load_rx():
        conn = get_db_connection()
        # Get pending prescriptions and the patient name
        rxs = conn.execute("""
            SELECT p.id, u.full_name, p.created_at 
            FROM prescriptions p 
            JOIN users u ON p.patient_id = u.id 
            WHERE p.status = 'Pending'
        """).fetchall()
        conn.close()

        rx_list.controls.clear()
        
        if not rxs:
            rx_list.controls.append(ft.Text("No pending prescriptions.", color="outline"))
        
        for rx in rxs:
            rx_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(f"Prescription #{rx['id']}", weight="bold"),
                            ft.Text(f"Patient: {rx['full_name']}"),
                            ft.Text(f"Date: {rx['created_at']}", size=12, color="outline"),
                        ], expand=True),
                        ft.ElevatedButton("Dispense", on_click=lambda e, rid=rx['id']: dispense(e, rid))
                    ]),
                    padding=15, border=ft.border.all(1, "outlineVariant"), border_radius=10, bgcolor="surface"
                )
            )

    def dispense(e, rx_id):
        # Update status to Approved
        conn = get_db_connection()
        conn.execute("UPDATE prescriptions SET status = 'Approved' WHERE id = ?", (rx_id,))
        conn.commit()
        conn.close()
        
        e.page.snack_bar = ft.SnackBar(ft.Text("Prescription Dispensed!"))
        e.page.snack_bar.open = True
        load_rx()
        e.page.update()

    load_rx()

    return ft.Column([
        ft.Text("Prescription Management", size=28, weight="bold"),
        ft.ElevatedButton("Refresh", icon=ft.Icons.REFRESH, on_click=lambda e: (load_rx(), e.page.update())),
        ft.Container(height=10),
        rx_list
    ], scroll=ft.ScrollMode.AUTO)