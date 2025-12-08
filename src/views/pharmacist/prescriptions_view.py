"""Prescriptions list and management with real database."""

import flet as ft
from datetime import datetime
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader

def PrescriptionsView():
    """List all prescriptions with filters."""
    
    # This holds the list of prescription cards
    prescriptions_container = ft.Column(spacing=10)
    
    # --- FILTERS ---
    # Dropdown to pick status
    status_filter = ft.Dropdown(
        label="Status",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Pending"),
            ft.dropdown.Option("Approved"),
            ft.dropdown.Option("Rejected"),
            ft.dropdown.Option("Dispensed"),
        ],
        value="All",
        width=150,
        # Making sure the border shows up in dark mode
        border_color="primary",
    )
    
    # Search box
    search_field = ft.TextField(
        hint_text="Search by patient name or prescription ID...",
        prefix_icon=ft.Icons.SEARCH,
        # Visible border for dark mode
        border_color="primary",
        expand=True,
    )
    
    # --- DB FUNCTION ---
    def get_prescriptions_from_db(status_val="All", search_query=""):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base query to grab everything
        query = """
            SELECT p.id, p.status, p.created_at, p.dosage, p.frequency, p.duration,
                   p.notes, p.pharmacist_notes, p.reviewed_date,
                   u.full_name as patient_name, u.id as patient_id,
                   m.name as medicine_name
            FROM prescriptions p
            LEFT JOIN users u ON p.patient_id = u.id
            LEFT JOIN medicines m ON p.medicine_id = m.id
            WHERE 1=1
        """
        
        params = []
        
        # Filter by status if selected
        if status_val != "All":
            query += " AND p.status = ?"
            params.append(status_val)
        
        # Filter by text search
        if search_query:
            query += " AND (u.full_name LIKE ? OR p.id LIKE ?)"
            params.append(f"%{search_query}%")
            params.append(f"%{search_query}%")
        
        # Sort newest first
        query += " ORDER BY p.created_at DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        # Convert DB rows to a nice list of dictionaries
        prescriptions = []
        for row in results:
            prescriptions.append({
                'id': row[0],
                'status': row[1],
                'created_at': row[2],
                'dosage': row[3],
                'frequency': row[4],
                'duration': row[5],
                'notes': row[6],
                'pharmacist_notes': row[7],
                'reviewed_date': row[8],
                'patient_name': row[9],
                'patient_id': row[10],
                'medicine': row[11],
            })
        
        return prescriptions
    
    # --- UI CARD CREATOR ---
    def create_prescription_card(rx):
        # Assign colors for badges
        status_colors = {
            "Pending": "tertiary",
            "Approved": "primary",
            "Rejected": "error",
            "Dispensed": "secondary",
        }
        
        status_color = status_colors.get(rx['status'], "outline")
        
        return ft.Container(
            content=ft.Column([
                # Top part: Header and Status
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
                            color="white",
                        ),
                        bgcolor=status_color,
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=15,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(height=10),
                
                # Medicine Details Row
                ft.Row([
                    ft.Column([
                        ft.Text("Medicine:", size=11, color="outline"),
                        ft.Text(rx['medicine'], size=13, weight="bold"),
                    ], spacing=2),
                    ft.VerticalDivider(width=20),
                    ft.Column([
                        ft.Text("Dosage:", size=11, color="outline"),
                        ft.Text(rx['dosage'], size=13),
                    ], spacing=2),
                    ft.VerticalDivider(width=20),
                    ft.Column([
                        ft.Text("Duration:", size=11, color="outline"),
                        ft.Text(f"{rx['duration']} days", size=13),
                    ], spacing=2),
                ], spacing=10, wrap=True),
                
                ft.Container(height=5),
                
                # Timestamp
                ft.Row([
                    ft.Icon(ft.Icons.ACCESS_TIME, size=14, color="outline"),
                    ft.Text(f"Submitted: {rx['created_at']}", size=12, color="outline"),
                ], spacing=5),
                
                # Notes Box (Only if notes exist)
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.NOTE, size=16, color="tertiary"),
                        ft.Text(rx['notes'], size=12, italic=True),
                    ], spacing=5),
                    visible=bool(rx.get('notes')),
                    bgcolor=ft.Colors.with_opacity(0.1, "tertiary"),
                    padding=8,
                    border_radius=5,
                ),
                
                # Action Buttons
                ft.Row([
                    ft.ElevatedButton(
                        "Review Details",
                        icon=ft.Icons.VISIBILITY,
                        bgcolor="primary",
                        color="onPrimary",
                        on_click=lambda e, rx_id=rx['id']: e.page.go(f"/pharmacist/prescription/{rx_id}"),
                    ),
                    ft.OutlinedButton(
                        "Quick Approve",
                        icon=ft.Icons.CHECK_CIRCLE,
                        disabled=rx['status'] != "Pending",
                        on_click=lambda e, rx_id=rx['id']: quick_approve(e, rx_id),
                    ),
                    ft.OutlinedButton(
                        "Quick Reject",
                        icon=ft.Icons.CANCEL,
                        disabled=rx['status'] != "Pending",
                        on_click=lambda e, rx_id=rx['id']: quick_reject(e, rx_id),
                    ),
                ], spacing=10, wrap=True),
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface", # Dark mode friendly
        )
    
    # --- ACTIONS ---
    def quick_approve(e, rx_id):
        user = AppState.get_user()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE prescriptions 
                SET status = 'Approved',
                    pharmacist_id = ?,
                    reviewed_date = ?
                WHERE id = ?
            """, (user['id'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), rx_id))
            
            cursor.execute("""
                INSERT INTO activity_log (user_id, action, details, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                user['id'],
                'prescription_approved',
                f"Quick approved prescription #{rx_id}",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            e.page.snack_bar = ft.SnackBar(content=ft.Text(f"Prescription #{rx_id} approved!"), bgcolor="primary")
            e.page.snack_bar.open = True
            
        except Exception as ex:
            conn.rollback()
            e.page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="error")
            e.page.snack_bar.open = True
        
        finally:
            conn.close()
            load_prescriptions(e)
    
    def quick_reject(e, rx_id):
        e.page.go(f"/pharmacist/prescription/{rx_id}")
    
    # --- LOADING LOGIC ---
    def load_prescriptions(e=None):
        prescriptions_container.controls.clear()
        
        status = status_filter.value
        query = search_field.value if search_field.value else ""
        
        all_prescriptions = get_prescriptions_from_db(status, query)
        
        if all_prescriptions:
            prescriptions_container.controls.append(
                ft.Text(f"Showing {len(all_prescriptions)} prescription(s)", 
                       size=14, color="outline", weight="bold")
            )
            for rx in all_prescriptions:
                prescriptions_container.controls.append(create_prescription_card(rx))
        else:
            # Empty State - CENTERED FIXED HERE
            prescriptions_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF, size=80, color="outline"),
                        ft.Text("No prescriptions found", size=18, color="outline"),
                        ft.Text("Try adjusting your filters", size=14, color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.alignment.center, # Forces alignment to center of screen area
                )
            )
        
        if e and hasattr(e, 'page'):
            e.page.update()
    
    # Initial load
    class FakePage:
        snack_bar = None
        def update(self): pass
        def go(self, route): pass
    
    load_prescriptions(type('Event', (), {'page': FakePage()})())
    
    # --- PAGE LAYOUT ---
    return ft.Column([
        NavigationHeader(
            "Prescription Management",
            "Review, approve, or reject patient prescriptions",
            show_back=False,
        ),
        
        ft.Container(
            content=ft.Column([
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
                    # REFRESH BUTTON REMOVED FROM HERE
                ], spacing=10),
                
                ft.Container(height=20),
                
                # List
                prescriptions_container,
            ], spacing=0),
            padding=20,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)