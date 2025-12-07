"""Patient prescriptions view with real database integration."""

import flet as ft
from state import AppState
from services.database import get_db_connection
import os
from datetime import datetime

def PrescriptionsView():
    """View and upload prescriptions with real data."""
    
    # Get current logged-in user
    user = AppState.get_user()
    if not user:
        return ft.Text("Please log in first", color="error")
    
    user_id = user['id']
    
    prescriptions_container = ft.Column(spacing=10)
    
    def load_prescriptions():
        """Load patient's prescriptions from database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                p.id,
                p.status,
                p.created_at,
                p.dosage,
                p.frequency,
                p.duration,
                p.doctor_name,
                p.notes,
                p.pharmacist_notes,
                p.reviewed_date,
                m.name as medicine_name
            FROM prescriptions p
            LEFT JOIN medicines m ON p.medicine_id = m.id
            WHERE p.patient_id = ?
            ORDER BY p.created_at DESC
        """, (user_id,))
        
        prescriptions = cursor.fetchall()
        conn.close()
        
        return prescriptions
    
    def get_status_color(status):
        """Get color for prescription status."""
        colors = {
            'Pending': 'tertiary',
            'Approved': 'primary',
            'Rejected': 'error',
            'Dispensed': 'outline'
        }
        return colors.get(status, 'outline')
    
    def format_date(date_str):
        """Format date string."""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%b %d, %Y")
        except:
            return date_str
    
    def create_prescription_card(prescription):
        """Create prescription card widget."""
        presc_id = prescription[0]
        status = prescription[1]
        created_at = format_date(prescription[2])
        dosage = prescription[3] or "N/A"
        frequency = prescription[4] or "N/A"
        duration = prescription[5] or "N/A"
        doctor = prescription[6] or "Not specified"
        notes = prescription[7] or ""
        pharm_notes = prescription[8] or ""
        medicine = prescription[10] or "Pending Review"
        
        status_color = get_status_color(status)
        
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Row([
                    ft.Column([
                        ft.Text(f"Prescription #{presc_id}", size=18, weight="bold"),
                        ft.Text(created_at, size=12, color="outline"),
                    ], spacing=2),
                    ft.Container(
                        content=ft.Text(
                            status,
                            size=12,
                            weight="bold",
                            color="onPrimaryContainer",
                        ),
                        bgcolor=ft.Colors.with_opacity(0.2, status_color),
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=15,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(),
                
                # Details
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.MEDICATION, size=20, color="primary"),
                        ft.Text(medicine, size=15, weight="bold"),
                    ], spacing=10),
                    
                    ft.Row([
                        ft.Column([
                            ft.Text("Dosage", size=11, color="outline"),
                            ft.Text(dosage, size=13, weight="bold"),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text("Frequency", size=11, color="outline"),
                            ft.Text(frequency, size=13, weight="bold"),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text("Duration", size=11, color="outline"),
                            ft.Text(f"{duration} days", size=13, weight="bold"),
                        ], spacing=2, expand=True),
                    ], spacing=10),
                    
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON, size=16, color="outline"),
                        ft.Text(f"Dr. {doctor}", size=13, color="outline"),
                    ], spacing=5),
                ], spacing=10),
                
                # Notes section (if any)
                ft.Column([
                    ft.Divider() if notes or pharm_notes else ft.Container(),
                    
                    ft.Column([
                        ft.Text("Patient Notes:", size=12, weight="bold", color="outline"),
                        ft.Text(notes, size=12),
                    ], spacing=5) if notes else ft.Container(),
                    
                    ft.Column([
                        ft.Text("Pharmacist Notes:", size=12, weight="bold", color="primary"),
                        ft.Text(pharm_notes, size=12),
                    ], spacing=5) if pharm_notes else ft.Container(),
                ], spacing=5),
                
                # Action buttons
                ft.Row([
                    ft.TextButton(
                        "View Details",
                        icon=ft.Icons.VISIBILITY,
                        on_click=lambda e, p=prescription: view_prescription_details(e, p)
                    ),
                ], alignment=ft.MainAxisAlignment.END),
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    def view_prescription_details(e, prescription):
        """Show prescription details dialog."""
        presc_id = prescription[0]
        status = prescription[1]
        created_at = format_date(prescription[2])
        dosage = prescription[3] or "N/A"
        frequency = prescription[4] or "N/A"
        duration = prescription[5] or "N/A"
        doctor = prescription[6] or "Not specified"
        notes = prescription[7] or "None"
        pharm_notes = prescription[8] or "None"
        reviewed = prescription[9]
        medicine = prescription[10] or "Pending Review"
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"Prescription #{presc_id}"),
            content=ft.Column([
                ft.Text(f"Status: {status}", weight="bold"),
                ft.Text(f"Created: {created_at}"),
                ft.Divider(),
                ft.Text("Prescription Details:", weight="bold"),
                ft.Text(f"Medicine: {medicine}"),
                ft.Text(f"Dosage: {dosage}"),
                ft.Text(f"Frequency: {frequency}"),
                ft.Text(f"Duration: {duration} days"),
                ft.Text(f"Prescribed by: Dr. {doctor}"),
                ft.Divider(),
                ft.Text(f"Patient Notes: {notes}"),
                ft.Text(f"Pharmacist Notes: {pharm_notes}"),
                ft.Text(f"Reviewed: {format_date(reviewed) if reviewed else 'Not yet'}"),
            ], spacing=10, tight=True, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Close", on_click=lambda e: close_dialog(e)),
            ],
        )
        
        e.page.dialog = dialog
        dialog.open = True
        e.page.update()
    
    def close_dialog(e):
        """Close dialog."""
        e.page.dialog.open = False
        e.page.update()
    
    def upload_prescription(e):
        """Handle prescription upload."""
        def file_picker_result(e: ft.FilePickerResultEvent):
            if e.files:
                file_path = e.files[0].path
                file_name = e.files[0].name
                
                # Show upload dialog
                show_upload_dialog(e.page, file_name, file_path)
        
        file_picker = ft.FilePicker(on_result=file_picker_result)
        e.page.overlay.append(file_picker)
        e.page.update()
        
        file_picker.pick_files(
            allowed_extensions=["jpg", "jpeg", "png", "pdf"],
            dialog_title="Select Prescription Image"
        )
    
    def show_upload_dialog(page, file_name, file_path):
        """Show dialog to add prescription details."""
        doctor_field = ft.TextField(label="Doctor Name", hint_text="e.g., Dr. Smith")
        notes_field = ft.TextField(
            label="Notes (Optional)",
            hint_text="Any special instructions...",
            multiline=True,
            min_lines=2,
            max_lines=4
        )
        
        def submit_prescription(e):
            doctor = doctor_field.value or "Not specified"
            notes = notes_field.value or ""
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                # Save prescription
                cursor.execute("""
                    INSERT INTO prescriptions 
                    (patient_id, image_path, doctor_name, notes, status, created_at)
                    VALUES (?, ?, ?, ?, 'Pending', ?)
                """, (user_id, file_path, doctor, notes, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
                conn.commit()
                
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Prescription uploaded successfully!"),
                    bgcolor="primary",
                )
                page.snack_bar.open = True
                
                close_dialog(e)
                refresh_prescriptions(e)
                
            except Exception as ex:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Upload failed: {str(ex)}"),
                    bgcolor="error",
                )
                page.snack_bar.open = True
            finally:
                conn.close()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Upload Prescription"),
            content=ft.Column([
                ft.Text(f"File: {file_name}", size=12, italic=True),
                ft.Divider(),
                doctor_field,
                notes_field,
            ], spacing=10, tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: close_dialog(e)),
                ft.ElevatedButton(
                    "Submit",
                    icon=ft.Icons.UPLOAD,
                    bgcolor="primary",
                    color="onPrimary",
                    on_click=submit_prescription
                ),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def refresh_prescriptions(e):
        """Refresh prescriptions list."""
        prescriptions = load_prescriptions()
        prescriptions_container.controls.clear()
        
        if prescriptions:
            for presc in prescriptions:
                prescriptions_container.controls.append(create_prescription_card(presc))
        else:
            prescriptions_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, size=80, color="outline"),
                        ft.Text("No prescriptions yet", size=18, color="outline"),
                        ft.Text("Upload your first prescription to get started", 
                               size=14, color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.alignment.center,
                )
            )
        
        e.page.update()
    
    # Initial load
    prescriptions = load_prescriptions()
    
    if prescriptions:
        for presc in prescriptions:
            prescriptions_container.controls.append(create_prescription_card(presc))
    else:
        prescriptions_container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, size=80, color="outline"),
                    ft.Text("No prescriptions yet", size=18, color="outline"),
                    ft.Text("Upload your first prescription to get started", 
                           size=14, color="outline"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=50,
                alignment=ft.alignment.center,
            )
        )
    
    return ft.Column([
        # Header
        ft.Row([
            ft.Text("My Prescriptions", size=28, weight="bold"),
            ft.ElevatedButton(
                "Upload Prescription",
                icon=ft.Icons.UPLOAD_FILE,
                bgcolor="primary",
                color="onPrimary",
                on_click=upload_prescription,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        ft.Text("View and manage your prescription history", size=14, color="outline"),
        
        ft.Container(height=20),
        
        # Filter/Status info
        ft.Row([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color="primary"),
                    ft.Text("Prescriptions are reviewed by pharmacists", size=12),
                ], spacing=5),
                padding=10,
                bgcolor=ft.Colors.with_opacity(0.1, "primary"),
                border_radius=5,
            ),
        ]),
        
        ft.Container(height=10),
        
        # Prescriptions list
        prescriptions_container,
    ], scroll=ft.ScrollMode.AUTO, spacing=0)