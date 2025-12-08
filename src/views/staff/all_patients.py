"""View all patients list for staff members."""

import flet as ft
from services.database import get_db_connection
from components.navigation_header import NavigationHeader

def AllPatientsView():
    """Display all registered patients."""
    
    patients_container = ft.Column(spacing=10)
    
    # Dropdown to pick sorting
    # Added border_color="primary" so it's visible in Dark Mode
    sort_dropdown = ft.Dropdown(
        label="Sort By",
        options=[
            ft.dropdown.Option("name_asc", "Name (A-Z)"),
            ft.dropdown.Option("name_desc", "Name (Z-A)"),
            ft.dropdown.Option("newest", "Newest First"),
        ],
        value="name_asc",
        width=200,
        border_color="primary", 
    )
    
    # Quick filter box
    # Added border_color="primary" here too
    search_field = ft.TextField(
        hint_text="Quick filter by name...",
        prefix_icon=ft.Icons.FILTER_LIST,
        expand=True,
        border_color="primary",
    )
    
    # --- ROW CREATOR ---
    # Makes the horizontal strip for each patient
    def create_patient_row(patient, index):
        return ft.Container(
            content=ft.Row([
                # Number
                ft.Text(f"#{index + 1}", weight="bold", width=40, color="primary"),
                
                # Avatar
                ft.Container(
                    content=ft.Icon(ft.Icons.PERSON, size=20, color="onSecondaryContainer"),
                    bgcolor="secondaryContainer", width=40, height=40, border_radius=20,
                    alignment=ft.alignment.center
                ),
                
                # Name & ID
                ft.Column([
                    ft.Text(patient['full_name'], weight="bold", size=14),
                    ft.Text(f"ID: {patient['id']}", size=11, color="outline"),
                ], width=200),
                
                # Contact info
                ft.Column([
                    ft.Text(patient['email'] or "-", size=12),
                    ft.Text(patient['phone'] or "-", size=12, color="outline"),
                ], expand=True),
                
                # Eye Button to see details
                ft.IconButton(
                    icon=ft.Icons.VISIBILITY,
                    tooltip="View Details",
                    icon_color="primary",
                    on_click=lambda e, pid=patient['id']: e.page.go(f"/staff/patient/{pid}")
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            bgcolor="surface",
            border_radius=8,
            border=ft.border.all(1, "outlineVariant"),
        )
    
    # --- LOAD DATA ---
    def load_patients(e=None):
        patients_container.controls.clear()
        
        # Get values from inputs
        txt = search_field.value.lower() if search_field.value else ""
        sort = sort_dropdown.value
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base query
        sql = "SELECT * FROM users WHERE role = 'Patient'"
        
        # Filter if text exists
        if txt:
            sql += f" AND LOWER(full_name) LIKE '%{txt}%'"
            
        # Apply sorting
        if sort == "name_asc": sql += " ORDER BY full_name ASC"
        elif sort == "name_desc": sql += " ORDER BY full_name DESC"
        elif sort == "newest": sql += " ORDER BY created_at DESC"
        
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            patients_container.controls.append(ft.Text(f"Total: {len(rows)} patients", color="outline"))
            for idx, row in enumerate(rows):
                # Map tuple to dict
                p = {
                    'id': row[0], 'full_name': row[4],
                    'email': row[6], 'phone': row[7]
                }
                patients_container.controls.append(create_patient_row(p, idx))
        else:
            patients_container.controls.append(
                ft.Container(
                    content=ft.Text("No patients found matching filter.", color="outline"),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
        
        if e: e.page.update()
        
    # Hack to load data when page first opens
    class Dummy: 
        page = None
    load_patients(None)
    
    # --- PAGE LAYOUT ---
    return ft.Column([
        NavigationHeader("All Patients", "Full directory of registered patients", show_back=False),
        
        ft.Container(
            padding=20,
            content=ft.Column([
                # Filter Bar Row
                ft.Row([
                    search_field,
                    sort_dropdown,
                    ft.IconButton(ft.Icons.REFRESH, on_click=load_patients, tooltip="Refresh")
                ]),
                
                ft.ElevatedButton("Apply Filter", on_click=load_patients, width=150, bgcolor="primary", color="onPrimary"),
                
                ft.Divider(),
                
                # The actual list
                patients_container
            ])
        )
    ], 
    scroll=ft.ScrollMode.AUTO, 
    spacing=0,
    # IMPORTANT: Forces content to top
    alignment=ft.MainAxisAlignment.START,
    expand=True
    )