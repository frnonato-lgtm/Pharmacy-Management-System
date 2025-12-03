import flet as ft

def StaffDashboard():
    """Simple greeting screen for staff."""
    return ft.Column([
        ft.Text("Staff Dashboard", size=28, weight="bold"),
        ft.Container(
            padding=20, bgcolor="surfaceVariant", border_radius=10,
            content=ft.Row([
                ft.Icon(ft.Icons.INFO, size=30, color="primary"),
                ft.Column([
                    ft.Text("Welcome to the Staff Portal", weight="bold"),
                    ft.Text("Use the sidebar to search for patient records."),
                ])
            ], spacing=20)
        )
    ])