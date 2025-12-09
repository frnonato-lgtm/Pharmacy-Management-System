"""Patient prescriptions view with enhanced submission form."""

import flet as ft
from state.app_state import AppState
from services.database import get_db_connection
from datetime import datetime

def PatientPrescriptionsView():
    """View patient's own prescriptions and submit new ones."""
    #
    # 1. Get the current user
    user = AppState.get_user()
    
    # 2. Get their prescription history from the DB
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
    
    # Helper to make the status badge look nice
    def create_prescription_card(rx):
        # Choose color based on status
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
                # Show notes only if they exist
                ft.Divider(height=10) if rx['notes'] else ft.Container(),
                ft.Text(rx['notes'], size=13, italic=True) if rx['notes'] else ft.Container(),
            ], spacing=8),
            padding=15,
            border=ft.border.all(1, color),
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.05, color),
        )
    
    # --- THIS IS THE POPUP FORM LOGIC ---
    def submit_prescription_dialog(e):
        print("Submit button clicked!") 
        
        # Define a consistent style for all inputs
        def create_input(label, multiline=False, keyboard_type=None):
            return ft.TextField(
                label=label,
                multiline=multiline,
                width=None,
                expand=True,
                border_color="outline",
                text_size=14,
                keyboard_type=keyboard_type if keyboard_type else None,
            )

        # Create the inputs with ALL necessary fields
        doctor_name = create_input("Doctor's Name *")
        medicine_name = create_input("Medicine Prescribed *")
        dosage = create_input("Dosage (e.g., 500ml, 2 tablets) *")
        frequency = create_input("Frequency (e.g., Once daily, Twice daily) *")
        duration = create_input("Duration (in days) *", keyboard_type=ft.KeyboardType.NUMBER)
        additional_notes = create_input("Additional Notes", multiline=True)
        
        # Error message label (hidden by default)
        error_text = ft.Text("", color="error", size=12)
        
        # What happens when they click "Submit" inside the popup
        def save_prescription(dialog_e):
            # Basic validation
            if not all([doctor_name.value, medicine_name.value, dosage.value, frequency.value, duration.value]):
                error_text.value = "Please fill in all required fields!"
                dialog_e.control.page.update()
                return
            
            # Validate duration is a number
            try:
                duration_days = int(duration.value)
            except:
                error_text.value = "Duration must be a number (in days)"
                dialog_e.control.page.update()
                return
            
            # Save to database
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Combine info into a structured notes string
                notes_text = f"Doctor: {doctor_name.value}\nMedicine: {medicine_name.value}\nDosage: {dosage.value}\nFrequency: {frequency.value}\nDuration: {duration_days} days\nNotes: {additional_notes.value or 'None'}"
                
                # Insert with structured fields
                cursor.execute("""
                    INSERT INTO prescriptions 
                    (patient_id, status, notes, created_at, dosage, frequency, duration, doctor_name)
                    VALUES (?, 'Pending', ?, ?, ?, ?, ?, ?)
                """, (
                    user['id'], 
                    notes_text, 
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    dosage.value,
                    frequency.value,
                    duration_days,
                    doctor_name.value
                ))
                
                conn.commit()
                conn.close()
                
                # Close the dialog
                dialog_e.control.page.close(prescription_form)
                
                # Show success snackbar
                dialog_e.control.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Prescription submitted! Waiting for review."),
                    bgcolor="primary"
                )
                dialog_e.control.page.snack_bar.open = True
                dialog_e.control.page.update()
                
                # Refresh the page to show the new item
                dialog_e.control.page.go("/patient/prescriptions")
                
            except Exception as ex:
                print(f"Error saving: {ex}")
                error_text.value = f"Error: {str(ex)}"
                dialog_e.control.page.update()

        # The actual Dialog Popup
        prescription_form = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.MEDICAL_SERVICES, color="primary"), 
                ft.Text("New Prescription")
            ]),
            bgcolor="surface", 
            shape=ft.RoundedRectangleBorder(radius=12),
            content=ft.Container(
                width=500,
                padding=10,
                content=ft.Column([
                    ft.Text("Enter details from your doctor's prescription:", size=13, color="outline"),
                    ft.Divider(height=10, color="transparent"),
                    doctor_name,
                    medicine_name,
                    dosage,
                    frequency,
                    duration,
                    ft.Text("Note: Medicine stock and pricing will be determined by the pharmacist", 
                           size=11, color="outline", italic=True),
                    additional_notes,
                    error_text,
                ], scroll=ft.ScrollMode.AUTO, tight=True)
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: e.page.close(prescription_form)),
                ft.ElevatedButton(
                    "Submit", 
                    icon=ft.Icons.SEND, 
                    bgcolor="primary", 
                    color="white", 
                    on_click=save_prescription
                ),
            ],
            actions_padding=20,
        )
        
        # Open it using the modern Flet way
        e.page.open(prescription_form)

    # --- MAIN PAGE LAYOUT ---
    return ft.Column([
        # Header Row
        ft.Row([
            ft.Icon(ft.Icons.MEDICAL_SERVICES, color="primary", size=32),
            ft.Column([
                ft.Text("My Prescriptions", size=28, weight="bold"),
                ft.Text("Submit prescription requests and track their status", size=14, color="outline"),
            ], spacing=5, expand=True),
            
            # The Button that triggers the popup
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
        
        # Info Box
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
        
        # The List Title
        ft.Text(f"Your Prescriptions ({len(prescriptions)})", size=20, weight="bold"),
        ft.Container(height=10),
        
        # The List Logic
        ft.Column([
            create_prescription_card(rx) for rx in prescriptions
        ], spacing=10) if prescriptions else ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, size=80, color="outline"),
                ft.Text("No prescriptions yet", size=18, color="outline"),
                ft.Text("Click the button above to submit one!", size=14, color="outline"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=50,
            alignment=ft.alignment.center,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)