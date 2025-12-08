"""Patient profile and settings view."""

import flet as ft
from state.app_state import AppState
from services.database import get_db_connection

def ProfileView():
    """Patient profile and account settings."""
    
    # Get the current logged in user
    user = AppState.get_user()
    
    # 1. FETCH DATA FROM DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user['id'],))
    
    # Convert row to dictionary for easy handling
    row = cursor.fetchone()
    user_data = dict(row) 
    
    conn.close()
    
    # --- CREATE DISPLAY WIDGETS ---
    
    # Helper to combine names
    def get_display_name():
        fname = user_data.get('full_name', '') or ""
        lname = user_data.get('last_name', '') or ""
        return f"{fname} {lname}".strip()

    # The header text using helper function
    txt_name_header = ft.Text(get_display_name(), size=24, weight="bold")
    txt_username_header = ft.Text(f"@{user_data['username']}", size=14, color="outline")
    
    # Other info fields
    txt_email = ft.Text(user_data['email'] or "Not provided", size=14, weight="bold")
    txt_phone = ft.Text(user_data['phone'] or "Not provided", size=14, weight="bold")
    txt_dob = ft.Text(user_data['dob'] or "Not provided", size=14, weight="bold")
    txt_address = ft.Text(user_data['address'] or "Not provided", size=14, weight="bold")

    # Helper to make the info rows look consistent
    def create_info_row(label, text_control, icon):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color="primary", size=24),
                ft.Column([
                    ft.Text(label, size=12, color="outline"),
                    text_control,
                ], spacing=2, expand=True),
            ], spacing=15),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
        )
    
    # --- EDIT PROFILE LOGIC ---
    def edit_profile(e):
        # Helper for consistent inputs
        def create_input(label, val, icon, multiline=False):
            return ft.TextField(
                label=label,
                value=val if val and val != "Not provided" else "",
                prefix_icon=icon,
                multiline=multiline,
                width=None, # Allow fill
                expand=True, # Force fill width
                border_color="outline"
            )

        # Create inputs
        first_name_field = create_input("First Name", user_data.get('full_name'), ft.Icons.PERSON)
        last_name_field = create_input("Last Name", user_data.get('last_name'), ft.Icons.PERSON)
        email_field = create_input("Email", user_data.get('email'), ft.Icons.EMAIL)
        phone_field = create_input("Phone", user_data.get('phone'), ft.Icons.PHONE)
        dob_field = create_input("Date of Birth (YYYY-MM-DD)", user_data.get('dob'), ft.Icons.CALENDAR_TODAY)
        address_field = create_input("Address", user_data.get('address'), ft.Icons.HOME, multiline=True)
        
        def save_changes(dialog_e):
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    UPDATE users 
                    SET full_name = ?, last_name = ?, email = ?, phone = ?, dob = ?, address = ?
                    WHERE id = ?
                """, (
                    first_name_field.value,
                    last_name_field.value,
                    email_field.value,
                    phone_field.value,
                    dob_field.value,
                    address_field.value,
                    user_data['id']
                ))
                conn.commit()
                
                # Update local data
                user_data['full_name'] = first_name_field.value
                user_data['last_name'] = last_name_field.value
                user_data['email'] = email_field.value
                user_data['phone'] = phone_field.value
                user_data['dob'] = dob_field.value
                user_data['address'] = address_field.value
                
                # Update UI
                txt_name_header.value = get_display_name()
                txt_email.value = email_field.value or "Not provided"
                txt_phone.value = phone_field.value or "Not provided"
                txt_dob.value = dob_field.value or "Not provided"
                txt_address.value = address_field.value or "Not provided"
                
                # Update AppState
                user['full_name'] = first_name_field.value
                AppState.set_user(user)

                dialog_e.page.close(edit_dialog)
                dialog_e.page.snack_bar = ft.SnackBar(content=ft.Text("Profile updated successfully!"), bgcolor="primary")
                dialog_e.page.snack_bar.open = True
                dialog_e.page.update()
                
            except Exception as ex:
                dialog_e.page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="error")
                dialog_e.page.snack_bar.open = True
                dialog_e.page.update()
            finally:
                conn.close()
        
        # Edit Profile Dialog
        edit_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([ft.Icon(ft.Icons.EDIT, color="primary"), ft.Text("Edit Profile")]),
            bgcolor="surface",
            shape=ft.RoundedRectangleBorder(radius=12),
            content=ft.Container(
                width=500,
                padding=10,
                content=ft.Column([
                    ft.Row([first_name_field, last_name_field], spacing=10),
                    email_field,
                    phone_field,
                    dob_field,
                    address_field,
                ], spacing=15, scroll=ft.ScrollMode.AUTO, tight=True)
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: e.page.close(edit_dialog)),
                ft.ElevatedButton("Save Changes", bgcolor="primary", color="white", on_click=save_changes),
            ],
            actions_padding=20,
        )
        e.page.open(edit_dialog)
    
    # --- PASSWORD CHANGE LOGIC ---
    def change_password(e):
        
        # Helper for consistent password inputs
        # Removed expand=True to prevent vertical stretching
        # Added width=float("inf") to ensure horizontal filling
        def create_pass_input(label, icon):
            return ft.TextField(
                label=label,
                password=True,
                can_reveal_password=True,
                prefix_icon=icon,
                width=float("inf"), 
                border_color="outline"
            )

        # Styled inputs
        current_password = create_pass_input("Current Password", ft.Icons.LOCK_OUTLINE)
        new_password = create_pass_input("New Password", ft.Icons.LOCK)
        confirm_password = create_pass_input("Confirm New Password", ft.Icons.LOCK_RESET)
        error_text = ft.Text("", color="error", size=12)
        
        def save_password(dialog_e):
            error_text.value = ""
            
            # Validation
            if not all([current_password.value, new_password.value, confirm_password.value]):
                error_text.value = "All fields are required"
                dialog_e.page.update()
                return
            
            if new_password.value != confirm_password.value:
                error_text.value = "New passwords do not match"
                dialog_e.page.update()
                return
            
            # Check DB
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE id = ?", (user_data['id'],))
            stored_password = cursor.fetchone()['password']
            
            if current_password.value != stored_password:
                error_text.value = "Current password is incorrect"
                conn.close()
                dialog_e.page.update()
                return
            
            # Update
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_password.value, user_data['id']))
            conn.commit()
            conn.close()
            
            dialog_e.page.close(pwd_dialog)
            dialog_e.page.snack_bar = ft.SnackBar(content=ft.Text("Password changed successfully!"), bgcolor="primary")
            dialog_e.page.snack_bar.open = True
            dialog_e.page.update()
        
        # Change Password Dialog
        pwd_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([ft.Icon(ft.Icons.LOCK_RESET, color="primary"), ft.Text("Change Password")]),
            bgcolor="surface",
            shape=ft.RoundedRectangleBorder(radius=12),
            content=ft.Container(
                width=500,
                padding=10,
                content=ft.Column([
                    current_password,
                    new_password,
                    confirm_password,
                    error_text,
                ], spacing=15, tight=True) # Reduced spacing to 15 to match
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: e.page.close(pwd_dialog)),
                ft.ElevatedButton("Change Password", bgcolor="primary", color="white", on_click=save_password),
            ],
            actions_padding=20,
        )
        e.page.open(pwd_dialog)
    
    # Navigation Helpers
    def view_medical_records(e):
        e.page.go("/patient/prescriptions")
    
    def logout(e):
        AppState.set_user(None)
        e.page.go("/")
    
    # --- PAGE LAYOUT ---
    return ft.Column([
        # Profile Header Card
        ft.Container(
            content=ft.Row([
                ft.Container(
                    width=100,
                    height=100,
                    bgcolor="primaryContainer",
                    border_radius=50,
                    content=ft.Icon(ft.Icons.PERSON, size=50, color="onPrimaryContainer"),
                    alignment=ft.alignment.center,
                ),
                ft.Column([
                    txt_name_header,
                    txt_username_header,
                    ft.Container(
                        content=ft.Text("Patient", size=12, weight="bold", color="onPrimaryContainer"),
                        bgcolor="primaryContainer",
                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                        border_radius=15,
                    ),
                ], spacing=5, expand=True),
                
                ft.ElevatedButton(
                    "Logout",
                    icon=ft.Icons.LOGOUT,
                    bgcolor="error",
                    color="onError",
                    on_click=logout,
                ),
            ], spacing=20),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
        
        ft.Container(height=20),
        
        ft.Text("Contact Information", size=20, weight="bold"),
        ft.Container(height=10),
        
        # Info Grid
        ft.Row([
            ft.Column([
                create_info_row("Email", txt_email, ft.Icons.EMAIL),
                create_info_row("Date of Birth", txt_dob, ft.Icons.CAKE),
            ], spacing=10, expand=True),
            
            ft.Column([
                create_info_row("Phone", txt_phone, ft.Icons.PHONE),
                create_info_row("Address", txt_address, ft.Icons.HOME),
            ], spacing=10, expand=True),
        ], spacing=15),
        
        ft.Container(height=20),
        ft.Divider(),
        ft.Container(height=10),
        
        # Account Actions List
        ft.Text("Account Actions", size=20, weight="bold"),
        ft.Container(height=10),
        
        ft.Column([
            # Edit Profile Button
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.EDIT, color="primary", size=24),
                    ft.Column([
                        ft.Text("Edit Profile", size=14, weight="bold"),
                        ft.Text("Update your personal information", size=12, color="outline"),
                    ], spacing=2, expand=True),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color="outline"),
                ], spacing=15),
                padding=15,
                border=ft.border.all(1, "outlineVariant"),
                border_radius=8,
                ink=True,
                on_click=edit_profile,
            ),
            
            # Change Password Button
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.LOCK, color="secondary", size=24),
                    ft.Column([
                        ft.Text("Change Password", size=14, weight="bold"),
                        ft.Text("Update your account password", size=12, color="outline"),
                    ], spacing=2, expand=True),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color="outline"),
                ], spacing=15),
                padding=15,
                border=ft.border.all(1, "outlineVariant"),
                border_radius=8,
                ink=True,
                on_click=change_password,
            ),
            
            # Medical Records Link
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.MEDICAL_INFORMATION, color="tertiary", size=24),
                    ft.Column([
                        ft.Text("Medical Records", size=14, weight="bold"),
                        ft.Text("View your prescription history", size=12, color="outline"),
                    ], spacing=2, expand=True),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color="outline"),
                ], spacing=15),
                padding=15,
                border=ft.border.all(1, "outlineVariant"),
                border_radius=8,
                ink=True,
                on_click=view_medical_records,
            ),
        ], spacing=10),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)