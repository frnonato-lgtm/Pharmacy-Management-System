"""Patient prescriptions view with submission form."""

import flet as ft
from state.app_state import AppState
from services.database import get_db_connection
from datetime import datetime

def PatientPrescriptionsView():
    """View patient's own prescriptions and submit new ones."""
    
    user = AppState.get_user()
    
    # Get patient's prescriptions
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, status, notes, created_at 
        FROM prescriptions 
        WHERE patient_id = ? 
        ORDER BY created_at DESC
    """, (user['id'],))
    prescriptions = cursor.fetchall()
    conn.close()
    
    def create_prescription_card(rx):
        """Create prescription status card."""
        status_colors = {
            "Pending": ("tertiary", ft.Icons.PENDING_ACTIONS),
            "Approved": ("primary", ft.Icons.CHECK_CIRCLE),
            "Rejected": ("error", ft.Icons.CANCEL),
        }
        color, icon = status_colors.get(rx['status'], ("outline", ft.Icons.INFO))
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text(f"Prescription #{rx['id']}", size=16, weight="bold"),
                        ft.Text(f"Submitted: {rx['created_at'][:16] if rx['created_at'] else 'N/A'}", 
                               size=12, color="outline"),
                    ], expand=True),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(icon, size=16, color=color),
                            ft.Text(rx['status'], weight="bold", color=color),
                        ], spacing=5),
                        bgcolor=ft.Colors.with_opacity(0.1, color),
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=15,
                    ),
                ]),
                ft.Divider(height=10) if rx['notes'] else ft.Container(),
                ft.Text(rx['notes'], size=13, italic=True) if rx['notes'] else ft.Container(),
            ], spacing=8),
            padding=15,
            border=ft.border.all(1, color),
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.05, color),
        )
    
    def submit_prescription_dialog(e):
        """Open prescription submission form."""
        
        doctor_name = ft.TextField(
            label="Doctor's Name *",
            hint_text="Dr. Juan Dela Cruz",
            width=300,
        )
        
        medicine_name = ft.TextField(
            label="Medicine Prescribed *",
            hint_text="Amoxicillin 500mg",
            width=300,
        )
        
        dosage = ft.TextField(
            label="Dosage Instructions *",
            hint_text="1 tablet 3 times daily",
            multiline=True,
            min_lines=2,
            width=300,
        )
        
        duration = ft.TextField(
            label="Duration *",
            hint_text="7 days",
            width=300,
        )
        
        additional_notes = ft.TextField(
            label="Additional Notes (Optional)",
            hint_text="Allergies, special instructions, etc.",
            multiline=True,
            min_lines=3,
            width=300,
        )
        
        error_text = ft.Text("", color="error", size=12)
        
        def save_prescription(dialog_e):
            """Save prescription to database."""
            error_text.value = ""
            
            # Validate
            if not all([doctor_name.value, medicine_name.value, dosage.value, duration.value]):
                error_text.value = "Please fill in all required fields"
                e.page.update()
                return
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                # Create notes text
                notes_text = f"""Doctor: {doctor_name.value}
Medicine: {medicine_name.value}
Dosage: {dosage.value}
Duration: {duration.value}
{f'Notes: {additional_notes.value}' if additional_notes.value else ''}"""
                
                cursor.execute("""
                    INSERT INTO prescriptions (patient_id, status, notes, created_at)
                    VALUES (?, 'Pending', ?, ?)
                """, (user['id'], notes_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
                conn.commit()
                conn.close()
                
                # Success
                prescription_dialog.open = False
                e.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Prescription submitted successfully! Awaiting pharmacist review."),
                    bgcolor="primary",
                )
                e.page.snack_bar.open = True
                e.page.update()
                
                # Refresh page
                e.page.go("/patient/prescriptions")
                
            except Exception as ex:
                conn.rollback()
                conn.close()
                error_text.value = f"Error: {str(ex)}"
                e.page.update()
        
        def close_dialog(dialog_e):
            prescription_dialog.open = False
            e.page.update()
        
        prescription_dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.MEDICAL_SERVICES, color="primary"),
                ft.Text("Submit Prescription Request"),
            ], spacing=10),
            content=ft.Column([
                ft.Text("Fill in your prescription details from your doctor", size=13, color="outline"),
                ft.Divider(),
                doctor_name,
                medicine_name,
                dosage,
                duration,
                additional_notes,
                error_text,
            ], spacing=15, width=350, height=500, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton(
                    "Submit Prescription",
                    icon=ft.Icons.SEND,
                    bgcolor="primary",
                    color="onPrimary",
                    on_click=save_prescription,
                ),
            ],
        )
        
        e.page.dialog = prescription_dialog
        prescription_dialog.open = True
        e.page.update()
    
    return ft.Column([
        # Header
        ft.Row([
            ft.Icon(ft.Icons.MEDICAL_SERVICES, color="primary", size=32),
            ft.Column([
                ft.Text("My Prescriptions", size=28, weight="bold"),
                ft.Text("Submit prescription requests and track their status", size=14, color="outline"),
            ], spacing=5, expand=True),
            ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD, color="white"),
                    ft.Text("Submit Prescription", color="white"),
                ], spacing=8),
                bgcolor="primary",
                style=ft.ButtonStyle(padding=15, shape=ft.RoundedRectangleBorder(radius=8)),
                on_click=submit_prescription_dialog,
            ),
        ], spacing=15),
        
        ft.Container(height=20),
        
        # How it works info
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, color="primary", size=20),
                    ft.Text("How it works:", size=14, weight="bold"),
                ]),
                ft.Text("1. Fill in prescription details from your doctor", size=13),
                ft.Text("2. Pharmacist will review and approve/reject", size=13),
                ft.Text("3. Once approved, you can order the medicine", size=13),
            ], spacing=8),
            padding=15,
            bgcolor=ft.Colors.with_opacity(0.1, "primary"),
            border_radius=8,
            border=ft.border.all(1, "primary"),
        ),
        
        ft.Container(height=20),
        
        # Prescriptions list
        ft.Column([
            ft.Text(f"Your Prescriptions ({len(prescriptions)})", size=20, weight="bold"),
            ft.Container(height=10),
            
            ft.Column([
                create_prescription_card(rx) for rx in prescriptions
            ], spacing=10) if prescriptions else ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, size=80, color="outline"),
                    ft.Text("No prescriptions yet", size=18, color="outline"),
                    ft.Text("Submit your first prescription request above", size=14, color="outline"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=50,
                alignment=ft.alignment.center,
            ),
        ]),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)