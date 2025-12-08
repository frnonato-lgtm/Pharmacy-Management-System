"""Enhanced patient search with detailed results."""

import flet as ft
from services.database import get_db_connection
from components.navigation_header import NavigationHeader

def StaffPatientSearch():
    """Search for patient records with detailed information."""
    
    # This column will hold all the search results
    results_container = ft.Column(spacing=15)
    
    # The search input box
    search_field = ft.TextField(
        label="Search Patient",
        hint_text="Enter name or phone number...",
        prefix_icon=ft.Icons.SEARCH,
        # Important: Setting border_color to primary makes it visible in Dark Mode!
        border_color="primary",
        expand=True,
        autofocus=True,
        text_size=14,
    )
    
    # --- CARD CREATOR ---
    # Creates the nice card for a single patient result
    def create_patient_card(patient):
        return ft.Container(
            content=ft.Column([
                # Top part: Avatar and Name
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.PERSON, size=30, color="onPrimaryContainer"),
                        width=60, height=60,
                        bgcolor="primaryContainer",
                        border_radius=30,
                        alignment=ft.alignment.center,
                    ),
                    ft.Column([
                        ft.Text(patient['full_name'], size=18, weight="bold"),
                        ft.Text(f"ID: {patient['id']}", size=12, color="outline"),
                        # A little badge to show they are a patient
                        ft.Container(
                            content=ft.Text("Patient", size=10, weight="bold", color="white"),
                            bgcolor="primary",
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            border_radius=5,
                        )
                    ], spacing=2, expand=True),
                    
                    # Arrow button to open the full details
                    ft.IconButton(
                        icon=ft.Icons.ARROW_FORWARD,
                        icon_color="primary",
                        on_click=lambda e, pid=patient['id']: e.page.go(f"/staff/patient/{pid}"),
                        tooltip="Open Record"
                    )
                ], spacing=15),
                
                ft.Divider(height=20, color="outlineVariant"),
                
                # Info Grid (Phone, Email, Date)
                ft.Row([
                    ft.Column([
                        ft.Row([ft.Icon(ft.Icons.PHONE, size=16, color="outline"), ft.Text(patient['phone'] or "N/A", size=13)], spacing=8),
                        ft.Row([ft.Icon(ft.Icons.EMAIL, size=16, color="outline"), ft.Text(patient['email'] or "N/A", size=13)], spacing=8),
                    ]),
                    ft.Column([
                        ft.Row([ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color="outline"), ft.Text(f"Reg: {patient['created_at'][:10]}", size=13)], spacing=8),
                    ])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
            ], spacing=5),
            padding=20,
            border_radius=12,
            bgcolor="surface", # Adapts to theme
            border=ft.border.all(1, "outlineVariant"),
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.05, "black"))
        )
    
    # --- SEARCH LOGIC ---
    def perform_search(e):
        # Clear previous results first
        results_container.controls.clear()
        term = search_field.value
        
        # If box is empty, show a prompt
        if not term:
            results_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH, size=50, color="outline"),
                        ft.Text("Enter a name or phone number", color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    padding=50
                )
            )
            e.page.update()
            return
        
        # Search the database
        conn = get_db_connection()
        cursor = conn.cursor()
        # SQL query: Find matching name OR phone number
        cursor.execute("""
            SELECT * FROM users 
            WHERE role = 'Patient' 
            AND (LOWER(full_name) LIKE ? OR phone LIKE ?)
            ORDER BY full_name ASC
        """, (f'%{term.lower()}%', f'%{term}%'))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            # Nothing found :(
            results_container.controls.append(
                ft.Container(
                    content=ft.Text("No patients found.", size=16, color="error"),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
        else:
            # Show how many we found
            results_container.controls.append(ft.Text(f"Found {len(rows)} results:", weight="bold"))
            # Loop through results and create cards
            for row in rows:
                # Convert tuple to dictionary
                p = {
                    'id': row[0], 'username': row[1], 'full_name': row[4],
                    'email': row[6], 'phone': row[7], 'created_at': row[10] or "N/A"
                }
                results_container.controls.append(create_patient_card(p))
        
        e.page.update()
    
    # --- PAGE LAYOUT ---
    return ft.Column([
        NavigationHeader("Patient Search", "Find patient records quickly", show_back=False),
        
        ft.Container(
            padding=20,
            content=ft.Column([
                # Search Bar Row
                ft.Row([
                    search_field,
                    ft.ElevatedButton(
                        "Search", 
                        icon=ft.Icons.SEARCH, 
                        height=50, 
                        bgcolor="primary", 
                        color="onPrimary",
                        on_click=perform_search
                    )
                ]),
                
                ft.Container(height=10),
                
                # The Results area
                results_container
            ])
        )
    ], 
    scroll=ft.ScrollMode.AUTO, 
    spacing=0,
    # IMPORTANT: This forces the content to start at the top, removing the weird gap!
    alignment=ft.MainAxisAlignment.START,
    expand=True
    )