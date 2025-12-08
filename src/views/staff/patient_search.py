"""Enhanced patient search with detailed results."""

import flet as ft
from services.database import get_db_connection
from components.navigation_header import NavigationHeader

def StaffPatientSearch():
    """Search for patient records with detailed information."""
    
    # Container for results
    results_container = ft.Column(spacing=10)
    
    # The search input box
    search_field = ft.TextField(
        label="Search by Name or Phone",
        hint_text="Enter patient name or phone number...",
        prefix_icon=ft.Icons.SEARCH,
        border_color="outline",
        expand=True,
        autofocus=True,
    )
    
    # Function to create the visual card for a patient
    def create_patient_card(patient):
        return ft.Container(
            content=ft.Column([
                # Header with icon and name
                ft.Row([
                    ft.Container(
                        width=60,
                        height=60,
                        bgcolor="primaryContainer",
                        border_radius=30,
                        content=ft.Icon(ft.Icons.PERSON, size=30, color="onPrimaryContainer"),
                        alignment=ft.alignment.center,
                    ),
                    ft.Column([
                        ft.Text(patient['full_name'], size=18, weight="bold"),
                        ft.Text(f"Patient ID: {patient['id']}", size=12, color="outline"),
                        # Badge
                        ft.Container(
                            content=ft.Text("Patient", size=11, color="white", weight="bold"),
                            bgcolor="primary",
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            border_radius=10,
                        ),
                    ], spacing=3, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.VISIBILITY,
                        icon_color="primary",
                        tooltip="View Full Details",
                        on_click=lambda e, pid=patient['id']: view_details(e, pid),
                    ),
                ], spacing=15),
                
                ft.Divider(height=10),
                
                # Info Grid
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.PHONE, size=20, color="secondary"),
                        ft.Column([
                            ft.Text("Phone", size=11, color="outline"),
                            ft.Text(patient['phone'] or "Not provided", size=13, weight="bold"),
                        ], spacing=2),
                    ], spacing=10),
                    
                    ft.Row([
                        ft.Icon(ft.Icons.EMAIL, size=20, color="secondary"),
                        ft.Column([
                            ft.Text("Email", size=11, color="outline"),
                            ft.Text(patient['email'] or "Not provided", size=13, weight="bold"),
                        ], spacing=2),
                    ], spacing=10),
                    
                    ft.Row([
                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=20, color="secondary"),
                        ft.Column([
                            ft.Text("Registered", size=11, color="outline"),
                            ft.Text(patient['created_at'][:10] if patient['created_at'] else "N/A", 
                                   size=13, weight="bold"),
                        ], spacing=2),
                    ], spacing=10),
                ], spacing=12),
                
                ft.Divider(height=10),
                
                # Buttons
                ft.Row([
                    ft.OutlinedButton(
                        "View Full Record",
                        icon=ft.Icons.ARTICLE,
                        on_click=lambda e, pid=patient['id']: view_details(e, pid),
                    ),
                    ft.OutlinedButton(
                        "View Prescriptions",
                        icon=ft.Icons.MEDICATION,
                        on_click=lambda e, pid=patient['id']: view_prescriptions(e, pid),
                    ),
                ], spacing=10),
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    # Navigation helpers
    def view_details(e, patient_id):
        e.page.go(f"/staff/patient/{patient_id}")
    
    def view_prescriptions(e, patient_id):
        e.page.snack_bar = ft.SnackBar(content=ft.Text("Viewing prescriptions..."), bgcolor="primary")
        e.page.snack_bar.open = True
        e.page.update()
        e.page.go(f"/staff/patient/{patient_id}/prescriptions")
    
    # Logic to run the search against the DB
    def perform_search(e):
        results_container.controls.clear()
        
        term = search_field.value
        if not term:
            # Show "Enter text" message if empty
            results_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH, size=60, color="outline"),
                        ft.Text("Enter a name or phone number to search", 
                               size=16, color="outline", text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                )
            )
            e.page.update()
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Search query matching Name OR Phone
        cursor.execute("""
            SELECT * FROM users 
            WHERE role = 'Patient' 
            AND (LOWER(full_name) LIKE ? OR phone LIKE ?)
            ORDER BY full_name ASC
        """, (f'%{term.lower()}%', f'%{term}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            # Show "No results" message
            results_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF, size=80, color="error"),
                        ft.Text("No patients found", size=18, weight="bold"),
                        ft.Text(f"No results for '{term}'", size=14, color="outline"),
                        ft.Text("Try searching with a different name or phone number", 
                               size=12, color="outline", italic=True),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                )
            )
        else:
            # Show results count
            results_container.controls.append(
                ft.Text(
                    f"Found {len(rows)} patient(s)",
                    size=14,
                    color="primary",
                    weight="bold",
                )
            )
            
            # Make a card for each found patient
            for row in rows:
                patient = {
                    'id': row[0],
                    'username': row[1],
                    'role': row[3],
                    'full_name': row[4],
                    'last_name': row[5],
                    'email': row[6],
                    'phone': row[7],
                    'dob': row[8],
                    'address': row[9],
                    'created_at': row[10] if len(row) > 10 else None,
                }
                results_container.controls.append(create_patient_card(patient))
        
        e.page.update()
    
    # --- PAGE LAYOUT ---
    return ft.Column([
        # Header - BACK BUTTON REMOVED
        NavigationHeader(
            "Patient Search",
            "Search and view patient records",
            show_back=False, # Set to False as requested
        ),
        
        ft.Container(
            content=ft.Column([
                # Search Bar Row
                ft.Row([
                    search_field,
                    ft.ElevatedButton(
                        "Search",
                        icon=ft.Icons.SEARCH,
                        bgcolor="primary",
                        color="white",
                        on_click=perform_search,
                        style=ft.ButtonStyle(
                            padding=15,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                ], spacing=10),
                
                ft.Container(height=10),
                
                # Info banner
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, color="secondary", size=20),
                        ft.Text(
                            "Search by patient name or phone number. You have read-only access.",
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
                
                # Where the results show up
                results_container,
            ], spacing=0),
            padding=20,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)