"""Detailed prescription review view."""

import flet as ft
from datetime import datetime
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader

def PrescriptionDetailView(prescription_id):
    """Detailed view for reviewing a single prescription."""
    
    # Get current pharmacist
    user = AppState.get_user()
    pharmacist_name = user['full_name'] if user else "Pharmacist"
    
    # Fetch prescription from database
    def get_prescription():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, 
                   u.full_name as patient_name,
                   u.email as patient_email,
                   u.phone as patient_phone,
                   m.name as medicine_name,
                   m.stock as medicine_stock,
                   m.price as medicine_price
            FROM prescriptions p
            LEFT JOIN users u ON p.patient_id = u.id
            LEFT JOIN medicines m ON p.medicine_id = m.id
            WHERE p.id = ?
        """, (prescription_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Convert to dictionary
        return {
            'id': row[0],
            'patient_id': row[1],
            'image_path': row[2],
            'status': row[3],
            'notes': row[4],
            'created_at': row[5],
            'medicine_id': row[6] if len(row) > 6 else None,
            'dosage': row[7] if len(row) > 7 else 'N/A',
            'frequency': row[8] if len(row) > 8 else 'N/A',
            'duration': row[9] if len(row) > 9 else 0,
            'doctor_name': row[10] if len(row) > 10 else 'N/A',
            'pharmacist_id': row[11] if len(row) > 11 else None,
            'pharmacist_notes': row[12] if len(row) > 12 else '',
            'reviewed_date': row[13] if len(row) > 13 else None,
            'patient_name': row[14] if len(row) > 14 else 'Unknown',
            'patient_email': row[15] if len(row) > 15 else 'N/A',
            'patient_phone': row[16] if len(row) > 16 else 'N/A',
            'medicine_name': row[17] if len(row) > 17 else 'N/A',
            'medicine_stock': row[18] if len(row) > 18 else 0,
            'medicine_price': row[19] if len(row) > 19 else 0.0,
        }
    
    rx = get_prescription()
    
    if not rx:
        return ft.Column([
            NavigationHeader("Prescription Not Found", show_back=True, back_route="/pharmacist/prescriptions"),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=100, color="error"),
                    ft.Text("Prescription not found", size=24, weight="bold"),
                    ft.Text(f"Prescription ID: {prescription_id}", color="outline"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                padding=50,
                expand=True,
            ),
        ])
    
    # Status colors
    status_colors = {
        "Pending": "tertiary",
        "Approved": "primary",
        "Rejected": "error",
        "Dispensed": "secondary",
    }
    status_color = status_colors.get(rx['status'], "outline")
    
    # Action buttons state
    notes_field = ft.TextField(
        label="Pharmacist Notes (Optional)",
        multiline=True,
        min_lines=3,
        max_lines=5,
        border_color="outline",
        value=rx['pharmacist_notes'] or "",
    )
    
    def approve_prescription(e):
        """Approve the prescription."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Update prescription status
            cursor.execute("""
                UPDATE prescriptions 
                SET status = 'Approved',
                    pharmacist_id = ?,
                    pharmacist_notes = ?,
                    reviewed_date = ?
                WHERE id = ?
            """, (user['id'], notes_field.value or "", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), prescription_id))
            
            # Log activity
            cursor.execute("""
                INSERT INTO activity_log (user_id, action, details, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                user['id'],
                'prescription_approved',
                f"Approved prescription #{prescription_id} for {rx['patient_name']}",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            conn.close()
            
            # Show success message
            e.page.snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color="white"),
                    ft.Text(f"Prescription #{prescription_id} approved successfully!", color="white"),
                ]),
                bgcolor="primary",
                duration=3000,
            )
            e.page.snack_bar.open = True
            
            # Navigate back to prescriptions list
            e.page.go("/pharmacist/prescriptions")
            
        except Exception as ex:
            conn.rollback()
            conn.close()
            
            e.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(ex)}"),
                bgcolor="error",
            )
            e.page.snack_bar.open = True
            e.page.update()
    
    def reject_prescription(e):
        """Reject the prescription."""
        if not notes_field.value:
            e.page.snack_bar = ft.SnackBar(
                content=ft.Text("Please provide a reason for rejection in notes."),
                bgcolor="error",
            )
            e.page.snack_bar.open = True
            e.page.update()
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Update prescription status
            cursor.execute("""
                UPDATE prescriptions 
                SET status = 'Rejected',
                    pharmacist_id = ?,
                    pharmacist_notes = ?,
                    reviewed_date = ?
                WHERE id = ?
            """, (user['id'], notes_field.value, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), prescription_id))
            
            # Log activity
            cursor.execute("""
                INSERT INTO activity_log (user_id, action, details, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                user['id'],
                'prescription_rejected',
                f"Rejected prescription #{prescription_id} for {rx['patient_name']}",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            conn.close()
            
            # Show success message
            e.page.snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.Icons.CANCEL, color="white"),
                    ft.Text(f"Prescription #{prescription_id} rejected.", color="white"),
                ]),
                bgcolor="error",
                duration=3000,
            )
            e.page.snack_bar.open = True
            
            # Navigate back
            e.page.go("/pharmacist/prescriptions")
            
        except Exception as ex:
            conn.rollback()
            conn.close()
            
            e.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(ex)}"),
                bgcolor="error",
            )
            e.page.snack_bar.open = True
            e.page.update()
    
    # Info card helper
    def info_card(title, content, icon, color="primary"):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=24),
                    ft.Text(title, size=14, color="outline", weight="bold"),
                ], spacing=10),
                ft.Container(height=5),
                ft.Text(str(content), size=16, weight="bold"),
            ], spacing=5),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
            bgcolor="surface",
            expand=True,
        )
    
    return ft.Column([
        # Navigation header
        NavigationHeader(
            f"Prescription #{prescription_id}",
            "Review prescription details and take action",
            show_back=True,
            back_route="/pharmacist/prescriptions"
        ),
        
        ft.Container(
            content=ft.Column([
                # Status badge
                ft.Row([
                    ft.Container(
                        content=ft.Text(
                            rx['status'],
                            size=16,
                            weight="bold",
                            color="white",
                        ),
                        bgcolor=status_color,
                        padding=ft.padding.symmetric(horizontal=20, vertical=10),
                        border_radius=20,
                    ),
                    ft.Text(f"Submitted: {rx['created_at']}", size=13, color="outline"),
                ], spacing=15),
                
                ft.Container(height=20),
                
                # Patient Information
                ft.Text("Patient Information", size=20, weight="bold"),
                ft.Row([
                    info_card(
                        "Patient Name",
                        rx['patient_name'],
                        ft.Icons.PERSON,
                        "primary"
                    ),
                    info_card(
                        "Contact",
                        rx['patient_email'] or "No email",
                        ft.Icons.EMAIL,
                        "secondary"
                    ),
                    info_card(
                        "Phone",
                        rx['patient_phone'] or "No phone",
                        ft.Icons.PHONE,
                        "tertiary"
                    ),
                ], spacing=15),
                
                ft.Container(height=20),
                
                # Prescription Details
                ft.Text("Prescription Details", size=20, weight="bold"),
                ft.Container(
                    content=ft.Column([
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
                                ft.Text(rx['dosage'], size=16, weight="bold"),
                            ], spacing=2, expand=True),
                            
                            ft.Column([
                                ft.Text("Frequency", size=12, color="outline"),
                                ft.Text(rx['frequency'], size=16, weight="bold"),
                            ], spacing=2, expand=True),
                            
                            ft.Column([
                                ft.Text("Duration", size=12, color="outline"),
                                ft.Text(f"{rx['duration']} days", size=16, weight="bold"),
                            ], spacing=2, expand=True),
                        ], spacing=20),
                        
                        ft.Divider(height=20),
                        
                        ft.Row([
                            ft.Column([
                                ft.Text("Prescribed by", size=12, color="outline"),
                                ft.Text(rx['doctor_name'], size=16, weight="bold"),
                            ], spacing=2, expand=True),
                            
                            ft.Column([
                                ft.Text("Current Stock", size=12, color="outline"),
                                ft.Text(
                                    f"{rx['medicine_stock']} units",
                                    size=16,
                                    weight="bold",
                                    color="error" if rx['medicine_stock'] < 10 else "primary"
                                ),
                            ], spacing=2, expand=True),
                            
                            ft.Column([
                                ft.Text("Unit Price", size=12, color="outline"),
                                ft.Text(f"₱{rx['medicine_price']:.2f}", size=16, weight="bold"),
                            ], spacing=2, expand=True),
                        ], spacing=20),
                        
                        # Doctor's notes
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.NOTE_ALT, size=20, color="tertiary"),
                                    ft.Text("Doctor's Notes", size=14, weight="bold"),
                                ], spacing=10),
                                ft.Text(
                                    rx['notes'] or "No additional notes provided",
                                    size=13,
                                    italic=not rx['notes'],
                                    color="outline" if not rx['notes'] else None,
                                ),
                            ], spacing=10),
                            bgcolor=ft.Colors.with_opacity(0.05, "tertiary"),
                            padding=15,
                            border_radius=8,
                            border=ft.border.all(1, "tertiary"),
                        ),
                    ], spacing=15),
                    padding=20,
                    border=ft.border.all(1, "outlineVariant"),
                    border_radius=10,
                    bgcolor="surface",
                ),
                
                ft.Container(height=20),
                
                # Pharmacist Review Section (only if pending)
                ft.Container(
                    content=ft.Column([
                        ft.Text("Pharmacist Review", size=20, weight="bold"),
                        
                        notes_field,
                        
                        ft.Container(height=10),
                        
                        ft.Row([
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, color="white"),
                                    ft.Text("Approve Prescription", color="white"),
                                ], spacing=10),
                                bgcolor="primary",
                                style=ft.ButtonStyle(
                                    padding=15,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=approve_prescription,
                            ),
                            
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.CANCEL, color="white"),
                                    ft.Text("Reject Prescription", color="white"),
                                ], spacing=10),
                                bgcolor="error",
                                style=ft.ButtonStyle(
                                    padding=15,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=reject_prescription,
                            ),
                            
                            ft.OutlinedButton(
                                "Cancel",
                                icon=ft.Icons.ARROW_BACK,
                                on_click=lambda e: e.page.go("/pharmacist/prescriptions"),
                                style=ft.ButtonStyle(
                                    padding=15,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                            ),
                        ], spacing=10, wrap=True),
                    ], spacing=15),
                    visible=rx['status'] == 'Pending',
                ) if rx['status'] == 'Pending' else ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=60, color="outline"),
                        ft.Text(
                            f"This prescription has been {rx['status'].lower()}",
                            size=16,
                            color="outline",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            f"Reviewed on: {rx.get('reviewed_date', 'N/A')}",
                            size=13,
                            color="outline",
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=30,
                    border=ft.border.all(1, "outlineVariant"),
                    border_radius=10,
                ),
            ], spacing=0),
            padding=20,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)