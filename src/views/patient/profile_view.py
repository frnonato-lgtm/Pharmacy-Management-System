"""Patient profile and settings view."""

import flet as ft
from state.app_state import AppState
from services.database import get_db_connection

def ProfileView():
    """Patient profile and account settings."""
    
    user = AppState.get_user()
    
    # Fetch full user details from database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user['id'],))
    user_data = cursor.fetchone()
    conn.close()
    
    def create_info_row(label, value, icon):
        """Create info display row."""
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color="primary", size=24),
                ft.Column([
                    ft.Text(label, size=12, color="outline"),
                    ft.Text(value or "Not provided", size=14, weight="bold"),
                ], spacing=2, expand=True),
            ], spacing=15),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
        )
    
    def edit_profile(e):
        """Open edit profile dialog."""
        
        # Text fields for editing
        full_name_field = ft.TextField(
            label="Full Name",
            value=user_data['full_name'],
            width=300,
        )
        
        email_field = ft.TextField(
            label="Email",
            value=user_data['email'] or "",
            width=300,
        )
        
        phone_field = ft.TextField(
            label="Phone",
            value=user_data['phone'] or "",
            width=300,
        )
        
        dob_field = ft.TextField(
            label="Date of Birth (YYYY-MM-DD)",
            value=user_data['dob'] or "",
            width=300,
        )
        
        address_field = ft.TextField(
            label="Address",
            value=user_data['address'] or "",
            multiline=True,
            min_lines=2,
            max_lines=3,
            width=300,
        )
        
        def save_changes(dialog_e):
            """Save profile changes to database."""
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET full_name = ?, email = ?, phone = ?, dob = ?, address = ?
                WHERE id = ?
            """, (
                full_name_field.value,
                email_field.value,
                phone_field.value,
                dob_field.value,
                address_field.value,
                user_data['id']
            ))
            
            conn.commit()
            conn.close()
            
            # Close dialog and show success message
            edit_dialog.open = False
            e.page.snack_bar = ft.SnackBar(
                content=ft.Text("Profile updated successfully!"),
                bgcolor="primary",
            )
            e.page.snack_bar.open = True
            e.page.update()
            
            # Refresh the page
            e.page.go("/patient/profile")
        
        def close_dialog(dialog_e):
            edit_dialog.open = False
            e.page.update()
        
        # Create dialog
        edit_dialog = ft.AlertDialog(
            title=ft.Text("Edit Profile"),
            content=ft.Column([
                full_name_field,
                email_field,
                phone_field,
                dob_field,
                address_field,
            ], spacing=15, width=350, height=400, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton(
                    "Save Changes",
                    bgcolor="primary",
                    color="onPrimary",
                    on_click=save_changes,
                ),
            ],
        )
        
        e.page.dialog = edit_dialog
        edit_dialog.open = True
        e.page.update()
    
    def change_password(e):
        """Open change password dialog."""
        
        current_password = ft.TextField(
            label="Current Password",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        
        new_password = ft.TextField(
            label="New Password",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        
        confirm_password = ft.TextField(
            label="Confirm New Password",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        
        error_text = ft.Text("", color="error", size=12)
        
        def save_password(dialog_e):
            """Save new password."""
            error_text.value = ""
            
            # Validate
            if not all([current_password.value, new_password.value, confirm_password.value]):
                error_text.value = "All fields are required"
                e.page.update()
                return
            
            if new_password.value != confirm_password.value:
                error_text.value = "New passwords do not match"
                e.page.update()
                return
            
            # Verify current password
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE id = ?", (user_data['id'],))
            stored_password = cursor.fetchone()['password']
            
            # For now, plain text comparison (in production, use hashing!)
            if current_password.value != stored_password:
                error_text.value = "Current password is incorrect"
                conn.close()
                e.page.update()
                return
            
            # Update password
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", 
                         (new_password.value, user_data['id']))
            conn.commit()
            conn.close()
            
            # Success
            pwd_dialog.open = False
            e.page.snack_bar = ft.SnackBar(
                content=ft.Text("Password changed successfully!"),
                bgcolor="primary",
            )
            e.page.snack_bar.open = True
            e.page.update()
        
        def close_dialog(dialog_e):
            pwd_dialog.open = False
            e.page.update()
        
        pwd_dialog = ft.AlertDialog(
            title=ft.Text("Change Password"),
            content=ft.Column([
                current_password,
                new_password,
                confirm_password,
                error_text,
            ], spacing=15, width=350),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton(
                    "Change Password",
                    bgcolor="primary",
                    color="onPrimary",
                    on_click=save_password,
                ),
            ],
        )
        
        e.page.dialog = pwd_dialog
        pwd_dialog.open = True
        e.page.update()
    
    def view_medical_records(e):
        """Navigate to prescriptions page."""
        e.page.go("/patient/prescriptions")
    
    def logout(e):
        """Handle user logout."""
        AppState.set_user(None)
        e.page.go("/")
    
    return ft.Column([
        # Profile header
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
                    ft.Text(user_data['full_name'], size=24, weight="bold"),
                    ft.Text(f"@{user_data['username']}", size=14, color="outline"),
                    ft.Container(
                        content=ft.Text("Patient", size=12, weight="bold", color="onPrimaryContainer"),
                        bgcolor="primaryContainer",
                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                        border_radius=15,
                    ),
                ], spacing=5, expand=True),
                
                # Logout button
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
        
        # Contact info grid
        ft.Row([
            ft.Column([
                create_info_row("Email", user_data['email'], ft.Icons.EMAIL),
                create_info_row("Date of Birth", user_data['dob'], ft.Icons.CAKE),
            ], spacing=10, expand=True),
            
            ft.Column([
                create_info_row("Phone", user_data['phone'], ft.Icons.PHONE),
                create_info_row("Address", user_data['address'], ft.Icons.HOME),
            ], spacing=10, expand=True),
        ], spacing=15),
        
        ft.Container(height=20),
        ft.Divider(),
        ft.Container(height=10),
        
        # Account Actions
        ft.Text("Account Actions", size=20, weight="bold"),
        ft.Container(height=10),
        
        ft.Column([
            # Edit Profile
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
            
            # Change Password
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
            
            # Medical Records
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