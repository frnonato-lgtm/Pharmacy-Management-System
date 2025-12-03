import flet as ft
from services.database import get_db_connection

def StaffPatientSearch():
    """Search for patient contact info."""
    results = ft.Column()

    def perform_search(e):
        term = e.control.value
        if not term:
            results.controls.clear()
            results.update()
            return

        conn = get_db_connection()
        # Search by name OR phone number
        rows = conn.execute(
            "SELECT * FROM users WHERE role='Patient' AND (full_name LIKE ? OR phone LIKE ?)", 
            (f'%{term}%', f'%{term}%')
        ).fetchall()
        conn.close()

        results.controls.clear()
        
        if not rows:
            results.controls.append(ft.Text("No records found.", color="error"))
        else:
            for row in rows:
                results.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Column([
                                ft.Text(row['full_name'], weight="bold", size=16),
                                ft.Text(f"Phone: {row['phone']}"),
                                ft.Text(f"Email: {row['email']}", color="outline"),
                            ])
                        )
                    )
                )
        results.update()

    return ft.Column([
        ft.Text("Patient Search", size=28, weight="bold"),
        ft.TextField(label="Search by Name or Phone...", prefix_icon=ft.Icons.SEARCH, on_change=perform_search),
        ft.Divider(),
        results
    ], scroll=ft.ScrollMode.AUTO)