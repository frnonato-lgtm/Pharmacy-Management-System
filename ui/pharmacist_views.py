import flet as ft

def PharmacistDashboard():
    return ft.Column([
        ft.Text("Pharmacist Dashboard", size=25, weight="bold"),
        ft.Text("Pending Validations: 2")
    ])

def PrescriptionsView():
    return ft.ListView(
        expand=True,
        controls=[
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON),
                title=ft.Text("Patient: Jane Doe"),
                subtitle=ft.Text("Prescription: Amoxicillin 500mg"),
                trailing=ft.ElevatedButton("Dispense", color="white", bgcolor="green")
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON),
                title=ft.Text("Patient: Mark Smith"),
                subtitle=ft.Text("Prescription: Paracetamol"),
                trailing=ft.ElevatedButton("Dispense", color="white", bgcolor="green")
            )
        ]
    )