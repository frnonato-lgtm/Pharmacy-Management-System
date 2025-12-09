"""Detailed prescription review view - With Editable Prescription Details."""

import flet as ft
from datetime import datetime
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader

def PrescriptionDetailView(prescription_id):
    """Detailed view for reviewing a single prescription."""
    
    # Get current pharmacist info for logging
    user = AppState.get_user()
    
    # A state variable to toggle between "View Mode" and "Edit Mode"
    is_editing = {"value": False}
    
    # Function to get data from the database
    def get_prescription():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # --- FIX: EXPLICIT COLUMNS ---
        # I am listing every column name here instead of using SELECT *
        # This prevents the bug where "Doctor Name" was showing up as "Duration"
        # because the database columns were in a different order than expected.
        cursor.execute("""
            SELECT 
                p.id,               -- 0
                p.patient_id,       -- 1
                p.status,           -- 2
                p.notes,            -- 3
                p.created_at,       -- 4
                p.medicine_id,      -- 5
                p.dosage,           -- 6
                p.frequency,        -- 7
                p.duration,         -- 8
                p.doctor_name,      -- 9
                p.pharmacist_notes, -- 10
                p.reviewed_date,    -- 11
                u.full_name,        -- 12 (patient name)
                u.email,            -- 13
                u.phone,            -- 14
                m.name,             -- 15 (medicine name)
                m.stock,            -- 16
                m.price             -- 17
            FROM prescriptions p
            LEFT JOIN users u ON p.patient_id = u.id
            LEFT JOIN medicines m ON p.medicine_id = m.id
            WHERE p.id = ?
        """, (prescription_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Return a dictionary so we can access data by name (easier to read)
        return {
            'id': row[0],
            'status': row[2],
            'notes': row[3],
            'created_at': row[4],
            'dosage': row[6] if row[6] else '',
            'frequency': row[7] if row[7] else '',
            'duration': row[8] if row[8] else 0, # Now guaranteed to be duration
            'doctor_name': row[9] if row[9] else '',
            'pharmacist_notes': row[10] if row[10] else '',
            'reviewed_date': row[11],
            'patient_name': row[12] or 'Unknown',
            'patient_email': row[13] or 'N/A',
            'patient_phone': row[14] or 'N/A',
            'medicine_name': row[15] or 'Not specified',
            'medicine_stock': row[16] if row[16] is not None else 0,
            'medicine_price': row[17] if row[17] is not None else 0.0,
        }
    
    # Load the data
    rx = get_prescription()
    
    # Safety check
    if not rx:
        return ft.Text("Prescription not found")
    
    # Colors for the status badge
    status_colors = {
        "Pending": "tertiary",
        "Approved": "primary",
        "Rejected": "error",
        "Dispensed": "secondary",
    }
    status_color = status_colors.get(rx['status'], "outline")
    
    # --- EDITABLE FIELDS ---
    # These text fields are used when the pharmacist clicks the "Edit" button
    medicine_field = ft.TextField(label="Medicine Name", value=rx['medicine_name'], border_color="outline")
    dosage_field = ft.TextField(label="Dosage", value=rx['dosage'], border_color="outline")
    frequency_field = ft.TextField(label="Frequency", value=rx['frequency'], border_color="outline")
    duration_field = ft.TextField(label="Duration (days)", value=str(rx['duration']), border_color="outline", keyboard_type=ft.KeyboardType.NUMBER)
    doctor_field = ft.TextField(label="Prescribed by", value=rx['doctor_name'], border_color="outline")
    
    # Field for pharmacist to write notes (always visible in pending state)
    pharmacist_notes_field = ft.TextField(
        label="Pharmacist Notes (Optional)",
        multiline=True,
        min_lines=3,
        border_color="outline",
        value=rx['pharmacist_notes'] or "",
    )
    
    # This container holds the details part of the screen (it swaps between View and Edit)
    prescription_container = ft.Column()
    
    # Logic to save changes if the pharmacist edits the details
    def save_prescription_details(e):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # --- FIX: RE-LINK MEDICINE ---
            # If the pharmacist corrected the medicine name, we search for the ID again.
            # This ensures the stock/price updates correctly.
            cursor.execute("SELECT id FROM medicines WHERE name LIKE ?", (f"%{medicine_field.value}%",))
            match = cursor.fetchone()
            new_med_id = match[0] if match else None
            
            # Update the database
            cursor.execute("""
                UPDATE prescriptions 
                SET medicine_id = ?, 
                    dosage = ?,
                    frequency = ?,
                    duration = ?,
                    doctor_name = ?
                WHERE id = ?
            """, (
                new_med_id,
                dosage_field.value,
                frequency_field.value,
                int(duration_field.value) if duration_field.value.isdigit() else 0,
                doctor_field.value,
                prescription_id
            ))
            
            conn.commit()
            conn.close()
            
            # Update the local variable so the UI refreshes immediately
            rx['medicine_name'] = medicine_field.value
            rx['dosage'] = dosage_field.value
            rx['frequency'] = frequency_field.value
            rx['duration'] = int(duration_field.value) if duration_field.value.isdigit() else 0
            rx['doctor_name'] = doctor_field.value
            
            # Turn off edit mode
            is_editing["value"] = False
            update_prescription_display(e)
            
            e.page.snack_bar = ft.SnackBar(content=ft.Text("Updated successfully!"), bgcolor="primary")
            e.page.snack_bar.open = True
            e.page.update()
            
        except Exception as ex:
            e.page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="error")
            e.page.snack_bar.open = True
            e.page.update()
    
    # Helper to toggle edit mode
    def toggle_edit_mode(e):
        is_editing["value"] = not is_editing["value"]
        update_prescription_display(e)
    
    # Function that draws the details box
    def update_prescription_display(e):
        medicine_stock = rx['medicine_stock']
        # Show red text if stock is low
        stock_color = "error" if medicine_stock < 10 else "primary"
        
        if is_editing["value"]:
            # --- EDIT MODE UI ---
            prescription_container.controls = [
                ft.Row([
                    ft.Icon(ft.Icons.MEDICATION, color="primary", size=32),
                    ft.Column([
                        ft.Text("Medicine", size=12, color="outline"),
                        medicine_field, # Using the TextField
                    ], spacing=2, expand=True),
                ], spacing=15),
                
                ft.Divider(height=20),
                
                ft.Row([
                    ft.Column([dosage_field], expand=True),
                    ft.Column([frequency_field], expand=True),
                    ft.Column([duration_field], expand=True),
                ], spacing=20),
                
                ft.Container(height=10),
                doctor_field,
                
                ft.Container(height=20),
                ft.Row([
                    ft.ElevatedButton("Save Changes", icon=ft.Icons.SAVE, bgcolor="primary", color="white", on_click=save_prescription_details),
                    ft.OutlinedButton("Cancel", icon=ft.Icons.CANCEL, on_click=toggle_edit_mode),
                ], spacing=10),
            ]
        else:
            # --- VIEW MODE UI ---
            prescription_container.controls = [
                ft.Row([
                    ft.Icon(ft.Icons.MEDICATION, color="primary", size=32),
                    ft.Column([
                        ft.Text("Medicine", size=12, color="outline"),
                        ft.Text(rx['medicine_name'], size=20, weight="bold"),
                    ], spacing=2),
                ], spacing=15),
                
                ft.Divider(height=20),
                
                ft.Row([
                    ft.Column([
                        ft.Text("Dosage", size=12, color="outline"),
                        ft.Text(rx['dosage'] or 'N/A', size=16, weight="bold"),
                    ], expand=True),
                    ft.Column([
                        ft.Text("Frequency", size=12, color="outline"),
                        ft.Text(rx['frequency'] or 'N/A', size=16, weight="bold"),
                    ], expand=True),
                    ft.Column([
                        ft.Text("Duration", size=12, color="outline"),
                        # Shows number of days correctly now
                        ft.Text(f"{rx['duration']} days", size=16, weight="bold"),
                    ], expand=True),
                ], spacing=20),
                
                ft.Divider(height=20),
                
                ft.Row([
                    ft.Column([
                        ft.Text("Prescribed by", size=12, color="outline"),
                        ft.Text(rx['doctor_name'] or 'N/A', size=16, weight="bold"),
                    ], expand=True),
                    ft.Column([
                        ft.Text("Current Stock", size=12, color="outline"),
                        ft.Text(f"{medicine_stock} units", size=16, weight="bold", color=stock_color),
                    ], expand=True),
                    ft.Column([
                        ft.Text("Unit Price", size=12, color="outline"),
                        ft.Text(f"₱{rx['medicine_price']:.2f}", size=16, weight="bold"),
                    ], expand=True),
                ], spacing=20),
                
                # Container for Doctor's Notes (Read Only)
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.NOTE_ALT, size=20, color="tertiary"), ft.Text("Patient/Doctor Notes", weight="bold")]),
                        ft.Text(rx['notes'] or "No additional notes", italic=True),
                    ], spacing=5),
                    bgcolor=ft.Colors.with_opacity(0.05, "tertiary"),
                    padding=15, border_radius=8,
                    border=ft.border.all(1, "tertiary")
                )
            ]
        
        # Refresh UI if the page is already loaded
        if e: e.page.update()
    
    # Logic for Approving
    def approve_prescription(e):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE prescriptions 
            SET status = 'Approved', pharmacist_id = ?, pharmacist_notes = ?, reviewed_date = ?
            WHERE id = ?
        """, (user['id'], pharmacist_notes_field.value, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), rx['id']))
        
        # Log the action
        cursor.execute("INSERT INTO activity_log (user_id, action, details, timestamp) VALUES (?, ?, ?, ?)", 
                      (user['id'], 'prescription_approved', f"Approved Rx #{rx['id']}", datetime.now()))
        
        conn.commit()
        conn.close()
        
        e.page.snack_bar = ft.SnackBar(content=ft.Text("Approved!"), bgcolor="primary")
        e.page.snack_bar.open = True
        e.page.go("/pharmacist/prescriptions")

    # Logic for Rejecting
    def reject_prescription(e):
        if not pharmacist_notes_field.value:
            e.page.snack_bar = ft.SnackBar(content=ft.Text("Please add a note explaining rejection"), bgcolor="error")
            e.page.snack_bar.open = True
            e.page.update()
            return
            
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE prescriptions 
            SET status = 'Rejected', pharmacist_id = ?, pharmacist_notes = ?, reviewed_date = ?
            WHERE id = ?
        """, (user['id'], pharmacist_notes_field.value, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), rx['id']))
        
        # Log the action
        cursor.execute("INSERT INTO activity_log (user_id, action, details, timestamp) VALUES (?, ?, ?, ?)", 
                      (user['id'], 'prescription_rejected', f"Rejected Rx #{rx['id']}", datetime.now()))
        
        conn.commit()
        conn.close()
        
        e.page.snack_bar = ft.SnackBar(content=ft.Text("Rejected."), bgcolor="error")
        e.page.snack_bar.open = True
        e.page.go("/pharmacist/prescriptions")

    # Call this once at startup to render the View Mode
    update_prescription_display(None)
    
    # Helper to make little info cards
    def info_card(title, value, icon, color):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=color),
                ft.Column([
                    ft.Text(title, size=11, color="outline"),
                    ft.Text(str(value), weight="bold")
                ], spacing=2)
            ]),
            padding=15, border=ft.border.all(1, "outlineVariant"), border_radius=8, expand=True
        )

    # --- MAIN PAGE STRUCTURE ---
    return ft.Column([
        # Header with back button
        NavigationHeader(f"Prescription #{prescription_id}", "Review details", show_back=True, back_route="/pharmacist/prescriptions"),
        
        ft.Container(
            content=ft.Column([
                # Status Bar
                ft.Row([
                    ft.Container(
                        content=ft.Text(rx['status'], color="white", weight="bold"),
                        bgcolor=status_color, padding=ft.padding.symmetric(horizontal=20, vertical=10), border_radius=20
                    ),
                    ft.Text(f"Submitted: {rx['created_at']}", color="outline")
                ], spacing=15),
                
                ft.Container(height=20),
                
                # Patient Info Section
                ft.Text("Patient Information", size=20, weight="bold"),
                ft.Row([
                    info_card("Patient Name", rx['patient_name'], ft.Icons.PERSON, "primary"),
                    info_card("Contact", rx['patient_email'], ft.Icons.EMAIL, "secondary"),
                    info_card("Phone", rx['patient_phone'], ft.Icons.PHONE, "tertiary"),
                ], spacing=15),
                
                ft.Container(height=20),
                
                # Details Section Header + Edit Button
                ft.Row([
                    ft.Text("Prescription Details", size=20, weight="bold", expand=True),
                    # Edit button only visible if status is Pending
                    ft.IconButton(icon=ft.Icons.EDIT, tooltip="Edit Details", on_click=toggle_edit_mode, visible=rx['status']=='Pending')
                ]),
                
                # The main details container (changes content based on edit mode)
                ft.Container(
                    content=prescription_container,
                    padding=20, border=ft.border.all(1, "outlineVariant"), border_radius=10, bgcolor="surface"
                ),
                
                ft.Container(height=20),
                
                # Action Section (Approve/Reject)
                ft.Container(
                    content=ft.Column([
                        ft.Text("Pharmacist Review", size=20, weight="bold"),
                        pharmacist_notes_field,
                        ft.Container(height=10),
                        ft.Row([
                            ft.ElevatedButton("Approve Prescription", icon=ft.Icons.CHECK_CIRCLE, bgcolor="primary", color="white", on_click=approve_prescription),
                            ft.ElevatedButton("Reject Prescription", icon=ft.Icons.CANCEL, bgcolor="error", color="white", on_click=reject_prescription),
                            ft.OutlinedButton("Cancel", icon=ft.Icons.ARROW_BACK, on_click=lambda e: e.page.go("/pharmacist/prescriptions"))
                        ], spacing=10)
                    ]),
                    visible=rx['status'] == 'Pending'
                ) if rx['status'] == 'Pending' else ft.Container(
                    # If not pending, show a simple info box
                    content=ft.Column([
                        ft.Icon(ft.Icons.INFO, size=40, color="outline"),
                        ft.Text(f"This prescription is {rx['status']}", size=16, color="outline")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=30, alignment=ft.alignment.center
                )
                
            ]),
            padding=20
        )
    ], scroll=ft.ScrollMode.AUTO, spacing=0)