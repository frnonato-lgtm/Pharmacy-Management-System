"""View all patients list for staff members."""

import flet as ft
from services.database import get_db_connection
from components.navigation_header import NavigationHeader

def AllPatientsView():
    """Display all registered patients."""
    
    patients_container = ft.Column(spacing=10)
    
    # Sort options
    sort_dropdown = ft.Dropdown(
        label="Sort By",
        options=[
            ft.dropdown.Option("name_asc", "Name (A-Z)"),
            ft.dropdown.Option("name_desc", "Name (Z-A)"),
            ft.dropdown.Option("recent", "Recently Registered"),
            ft.dropdown.Option("oldest", "Oldest First"),
        ],
        value="name_asc",
        width=200,
    )
    
    search_field = ft.TextField(
        hint_text="Quick filter by name...",
        prefix_icon=ft.Icons.FILTER_LIST,
        border_color="outline",
        expand=True,
    )
    
    def create_patient_row(patient, index):
        """Create a patient list row."""
        return ft.Container(
            content=ft.Row([
                # Number
                ft.Container(
                    content=ft.Text(str(index + 1), size=16, weight="bold", color="primary"),
                    width=40,
                ),
                
                # Avatar
                ft.Container(
                    width=50,
                    height=50,
                    bgcolor="primaryContainer",
                    border_radius=25,
                    content=ft.Icon(ft.Icons.PERSON, size=24, color="onPrimaryContainer"),
                    alignment=ft.alignment.center,
                ),
                
                # Patient info
                ft.Column([
                    ft.Text(patient['full_name'], size=15, weight="bold"),
                    ft.Text(f"ID: {patient['id']}", size=11, color="outline"),
                ], spacing=2, expand=True),
                
                # Contact
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.PHONE, size=14, color="secondary"),
                        ft.Text(patient['phone'] or "No phone", size=12),
                    ], spacing=5),
                    ft.Row([
                        ft.Icon(ft.Icons.EMAIL, size=14, color="secondary"),
                        ft.Text(patient['email'] or "No email", size=12),
                    ], spacing=5),
                ], spacing=3, expand=True),
                
                # Registration date
                ft.Column([
                    ft.Text("Registered", size=10, color="outline"),
                    ft.Text(
                        patient['created_at'][:10] if patient['created_at'] else "N/A",
                        size=12,
                        weight="bold",
                    ),
                ], spacing=2),
                
                # Actions
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.VISIBILITY,
                        icon_color="primary",
                        tooltip="View Details",
                        on_click=lambda e, pid=patient['id']: e.page.go(f"/staff/patient/{pid}"),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SEARCH,
                        icon_color="secondary",
                        tooltip="Search This Patient",
                        on_click=lambda e, name=patient['full_name']: search_specific(e, name),
                    ),
                ], spacing=5),
            ], spacing=10, alignment=ft.MainAxisAlignment.START),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
            bgcolor="surface",
        )
    
    def search_specific(e, patient_name):
        """Pre-fill search with patient name."""
        e.page.go(f"/staff/search?q={patient_name}")
    
    def load_patients(e=None):
        """Load all patients from database."""
        patients_container.controls.clear()
        
        filter_term = search_field.value.lower() if search_field.value else ""
        sort_by = sort_dropdown.value
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query based on sort
        query = "SELECT * FROM users WHERE role = 'Patient'"
        
        if filter_term:
            query += f" AND LOWER(full_name) LIKE '%{filter_term}%'"
        
        if sort_by == "name_asc":
            query += " ORDER BY full_name ASC"
        elif sort_by == "name_desc":
            query += " ORDER BY full_name DESC"
        elif sort_by == "recent":
            query += " ORDER BY created_at DESC"
        elif sort_by == "oldest":
            query += " ORDER BY created_at ASC"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            # Show count
            patients_container.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.PEOPLE, color="primary", size=24),
                    ft.Text(
                        f"Showing {len(rows)} patient(s)",
                        size=16,
                        weight="bold",
                    ),
                ], spacing=10)
            )
            
            patients_container.controls.append(ft.Divider(height=10))
            
            # Create patient rows
            for idx, row in enumerate(rows):
                patient = {
                    'id': row[0],
                    'username': row[1],
                    'full_name': row[4],
                    'email': row[6],
                    'phone': row[7],
                    'created_at': row[10] if len(row) > 10 else None,
                }
                patients_container.controls.append(create_patient_row(patient, idx))
        else:
            patients_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.PERSON_OFF, size=80, color="outline"),
                        ft.Text("No patients found", size=18, color="outline"),
                        ft.Text("Try adjusting your filter", size=14, color="outline", italic=True),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                )
            )
        
        if e and hasattr(e, 'page'):
            e.page.update()
    
    # Initial load
    class FakePage:
        def update(self): pass
        def go(self, route): pass
    load_patients(type('Event', (), {'page': FakePage()})())
    
    return ft.Column([
        NavigationHeader(
            "All Patients",
            "View complete list of registered patients",
            show_back=True,
            back_route="/dashboard"
        ),
        
        ft.Container(
            content=ft.Column([
                # Filters and controls
                ft.Row([
                    search_field,
                    sort_dropdown,
                    ft.ElevatedButton(
                        "Apply",
                        icon=ft.Icons.CHECK,
                        bgcolor="primary",
                        color="white",
                        on_click=load_patients,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        icon_color="primary",
                        tooltip="Refresh List",
                        on_click=load_patients,
                    ),
                ], spacing=10),
                
                ft.Container(height=10),
                
                # Info banner
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, color="secondary", size=20),
                        ft.Text(
                            "Click on a patient to view their full details. You have read-only access.",
                            size=12,
                            color="outline",
                        ),
                    ], spacing=10),
                    bgcolor=ft.Colors.with_opacity(0.05, "secondary"),
                    padding=12,
                    border_radius=8,
                    border=ft.border.all(1, "secondary"),
                ),
                
                ft.Container(height=20),
                
                # Patients list
                patients_container,
            ], spacing=0),
            padding=20,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)