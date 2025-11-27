import flet as ft
from database import get_db_connection

def StaffDashboard():
    return ft.Column([
        ft.Text("Staff Dashboard", size=25, weight="bold"),
        ft.Container(
            padding=20, bgcolor="primaryContainer", border_radius=10,
            content=ft.Column([
                ft.Icon(ft.Icons.INFO, size=30, color="primary"),
                ft.Text("Welcome to the Staff Portal.", weight="bold", color="onPrimaryContainer"),
                ft.Text("Use the sidebar to search for patient records.", color="onPrimaryContainer")
            ])
        )
    ])

def StaffPatientSearch():
    results_container = ft.Column()

    def perform_search(e):
        search_term = e.control.value
        if not search_term:
            results_container.controls.clear()
            results_container.update()
            return

        conn = get_db_connection()
        query = "SELECT * FROM users WHERE role='Patient' AND (full_name LIKE ? OR phone LIKE ?)"
        params = (f'%{search_term}%', f'%{search_term}%')
        rows = conn.execute(query, params).fetchall()
        conn.close()

        results_container.controls.clear()
        
        if not rows:
            results_container.controls.append(ft.Text("No records found."))
        else:
            for row in rows:
                patient_card = ft.Card(
                    color="surfaceVariant",
                    content=ft.Container(
                        padding=15,
                        content=ft.Column([
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.PERSON, color="primary"),
                                title=ft.Text(row['full_name'], weight="bold"),
                                subtitle=ft.Text(f"Phone: {row['phone'] if row['phone'] else 'N/A'}"),
                            ),
                            ft.Text(f"Address: {row['address'] if row['address'] else 'N/A'}", size=12, color="outline"),
                            ft.Text(f"DOB: {row['dob'] if row['dob'] else 'N/A'}", size=12, color="outline"),
                        ])
                    )
                )
                results_container.controls.append(patient_card)
        
        results_container.update()

    return ft.Column([
        ft.Text("Patient Search", size=25, weight="bold"),
        ft.TextField(
            label="Search by Name or Phone Number", 
            prefix_icon=ft.Icons.SEARCH, 
            on_change=perform_search
        ),
        ft.Divider(),
        results_container
    ], scroll=ft.ScrollMode.AUTO)