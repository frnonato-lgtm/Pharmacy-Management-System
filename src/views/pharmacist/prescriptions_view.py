"""Prescriptions list and management."""

import flet as ft
from services.database import get_db_connection

def PrescriptionsView():
    """List all prescriptions with filters."""
    
    prescriptions_container = ft.Column(spacing=10)
    
    # Filter controls
    status_filter = ft.Dropdown(
        label="Status",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Pending"),
            ft.dropdown.Option("Approved"),
            ft.dropdown.Option("Rejected"),
        ],
        value="All",
        width=150,
    )
    
    search_field = ft.TextField(
        hint_text="Search by patient name or prescription ID...",
        prefix_icon=ft.Icons.SEARCH,
        border_color="outline",
        expand=True,
    )
    
    def get_mock_prescriptions():
        """Get mock prescriptions (replace with real DB later)."""
        return [
            {
                "id": 1234,
                "patient_name": "John Doe",
                "patient_id": 101,
                "doctor_name": "Dr. Smith",
                "medicine": "Amoxicillin 500mg",
                "dosage": "1 tablet 3x daily",
                "duration": "7 days",
                "status": "Pending",
                "date": "2025-11-26 14:30",
                "notes": "Patient has penicillin allergy - verify substitute",
            },
            {
                "id": 1235,
                "patient_name": "Jane Smith",
                "patient_id": 102,
                "doctor_name": "Dr. Johnson",
                "medicine": "Paracetamol 500mg",
                "dosage": "2 tablets every 6 hours",
                "duration": "5 days",
                "status": "Pending",
                "date": "2025-11-26 13:15",
                "notes": "",
            },
            {
                "id": 1236,
                "patient_name": "Robert Johnson",
                "patient_id": 103,
                "doctor_name": "Dr. Williams",
                "medicine": "Ibuprofen 400mg",
                "dosage": "1 tablet every 8 hours",
                "duration": "10 days",
                "status": "Approved",
                "date": "2025-11-26 10:00",
                "notes": "Approved by Dr. Chen",
            },
            {
                "id": 1237,
                "patient_name": "Emily Davis",
                "patient_id": 104,
                "doctor_name": "Dr. Brown",
                "medicine": "Cetirizine 10mg",
                "dosage": "1 tablet once daily",
                "duration": "14 days",
                "status": "Rejected",
                "date": "2025-11-25 16:45",
                "notes": "Invalid doctor signature",
            },
        ]
    
    def create_prescription_card(rx):
        """Create prescription card."""
        status_colors = {
            "Pending": "tertiary",
            "Approved": "primary",
            "Rejected": "error",
        }
        
        status_color = status_colors.get(rx['status'], "outline")
        
        return ft.Container(
            content=ft.Column([
                # Header row
                ft.Row([
                    ft.Column([
                        ft.Text(f"Prescription #{rx['id']}", size=16, weight="bold"),
                        ft.Text(f"Patient: {rx['patient_name']} (ID: {rx['patient_id']})", 
                               size=13, color="outline"),
                    ], spacing=2, expand=True),
                    ft.Container(
                        content=ft.Text(
                            rx['status'],
                            size=12,
                            weight="bold",
                            color=f"on{status_color.capitalize()}Container" if status_color != "outline" else "outline",
                        ),
                        bgcolor=ft.Colors.with_opacity(0.2, status_color),
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=15,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(height=10),
                
                # Prescription details
                ft.Row([
                    ft.Column([
                        ft.Text("Prescribed by:", size=11, color="outline"),
                        ft.Text(rx['doctor_name'], size=13, weight="bold"),
                    ], spacing=2),
                    ft.VerticalDivider(width=20),
                    ft.Column([
                        ft.Text("Medicine:", size=11, color="outline"),
                        ft.Text(rx['medicine'], size=13, weight="bold"),
                    ], spacing=2),
                    ft.VerticalDivider(width=20),
                    ft.Column([
                        ft.Text("Dosage:", size=11, color="outline"),
                        ft.Text(rx['dosage'], size=13),
                    ], spacing=2),
                ], spacing=10, wrap=True),
                
                ft.Container(height=5),
                
                ft.Row([
                    ft.Icon(ft.Icons.ACCESS_TIME, size=14, color="outline"),
                    ft.Text(f"Submitted: {rx['date']}", size=12, color="outline"),
                ], spacing=5),
                
                # Notes if any
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.NOTE, size=16, color="tertiary"),
                        ft.Text(rx['notes'], size=12, italic=True),
                    ], spacing=5),
                    visible=bool(rx['notes']),
                    bgcolor=ft.Colors.with_opacity(0.1, "tertiary"),
                    padding=8,
                    border_radius=5,
                ),
                
                # Action buttons
                ft.Row([
                    ft.ElevatedButton(
                        "Review Details",
                        icon=ft.Icons.VISIBILITY,
                        bgcolor="primary",
                        color="onPrimary",
                        on_click=lambda e, rx_id=rx['id']: e.page.go(f"/pharmacist/prescription/{rx_id}"),
                    ),
                    ft.OutlinedButton(
                        "Approve",
                        icon=ft.Icons.CHECK_CIRCLE,
                        disabled=rx['status'] != "Pending",
                        on_click=lambda e: approve_prescription(e, rx['id']),
                    ),
                    ft.OutlinedButton(
                        "Reject",
                        icon=ft.Icons.CANCEL,
                        disabled=rx['status'] != "Pending",
                        on_click=lambda e: reject_prescription(e, rx['id']),
                    ),
                ], spacing=10, wrap=True),
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    def approve_prescription(e, rx_id):
        """Approve prescription."""
        e.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Prescription #{rx_id} approved!"),
            bgcolor="primary",
        )
        e.page.snack_bar.open = True
        e.page.update()
        load_prescriptions(e)
    
    def reject_prescription(e, rx_id):
        """Reject prescription."""
        e.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Prescription #{rx_id} rejected."),
            bgcolor="error",
        )
        e.page.snack_bar.open = True
        e.page.update()
        load_prescriptions(e)
    
    def load_prescriptions(e=None):
        """Load and filter prescriptions."""
        prescriptions_container.controls.clear()
        
        all_prescriptions = get_mock_prescriptions()
        
        # Apply filters
        status = status_filter.value
        query = search_field.value.lower() if search_field.value else ""
        
        if status != "All":
            all_prescriptions = [rx for rx in all_prescriptions if rx['status'] == status]
        
        if query:
            all_prescriptions = [
                rx for rx in all_prescriptions
                if query in rx['patient_name'].lower() or query in str(rx['id'])
            ]
        
        if all_prescriptions:
            prescriptions_container.controls.append(
                ft.Text(f"Showing {len(all_prescriptions)} prescription(s)", 
                       size=14, color="outline", weight="bold")
            )
            for rx in all_prescriptions:
                prescriptions_container.controls.append(create_prescription_card(rx))
        else:
            prescriptions_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF, size=80, color="outline"),
                        ft.Text("No prescriptions found", size=18, color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                )
            )
        
        if e:
            e.page.update()
    
    # Initial load
    class FakePage:
        snack_bar = None
        def update(self): pass
    load_prescriptions(type('Event', (), {'page': FakePage()})())
    
    return ft.Column([
        ft.Row([
            ft.Icon(ft.Icons.ASSIGNMENT, color="primary", size=32),
            ft.Text("Prescription Management", size=28, weight="bold"),
        ], spacing=10),
        ft.Text("Review, approve, or reject patient prescriptions", size=14, color="outline"),
        
        ft.Container(height=20),
        
        # Filters
        ft.Row([
            search_field,
            status_filter,
            ft.ElevatedButton(
                "Filter",
                icon=ft.Icons.FILTER_ALT,
                bgcolor="primary",
                color="onPrimary",
                on_click=load_prescriptions,
            ),
        ], spacing=10),
        
        ft.Container(height=20),
        
        # Prescriptions list
        prescriptions_container,
    ], scroll=ft.ScrollMode.AUTO, spacing=0)