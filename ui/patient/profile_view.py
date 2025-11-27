"""Patient profile and settings view."""

import flet as ft
from state import AppState
from database import get_db_connection

def ProfileView():
    """Patient profile and account settings."""
    
    user = AppState.get_user()
    
    # Fetch full user details from database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user['id'],))
    user_data = cursor.fetchone()
    conn.close()
    
    def create_info_field(label, value, icon):
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
                    ft.Text(user_data['username'], size=14, color="outline"),
                    ft.Text(f"Role: {user_data['role']}", size=13, color="primary", weight="bold"),
                ], spacing=5),
            ], spacing=20),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
        
        ft.Container(height=20),
        
        ft.Text("Personal Information", size=20, weight="bold"),
        ft.Container(height=10),
        
        # Personal info grid
        ft.Row([
            ft.Column([
                create_info_field("Full Name", user_data['full_name'], ft.Icons.PERSON),
                create_info_field("Email", user_data['email'], ft.Icons.EMAIL),
                create_info_field("Date of Birth", user_data['dob'], ft.Icons.CAKE),
            ], spacing=10, expand=True),
            
            ft.Column([
                create_info_field("Username", user_data['username'], ft.Icons.ACCOUNT_CIRCLE),
                create_info_field("Phone", user_data['phone'], ft.Icons.PHONE),
                create_info_field("Address", user_data['address'], ft.Icons.HOME),
            ], spacing=10, expand=True),
        ], spacing=15),
        
        ft.Container(height=20),
        ft.Divider(),
        ft.Container(height=10),
        
        # Action buttons
        ft.Text("Account Actions", size=20, weight="bold"),
        ft.Container(height=10),
        
        ft.Row([
            ft.ElevatedButton(
                "Edit Profile",
                icon=ft.Icons.EDIT,
                bgcolor="primary",
                color="onPrimary",
            ),
            ft.OutlinedButton(
                "Change Password",
                icon=ft.Icons.LOCK,
            ),
            ft.OutlinedButton(
                "Medical Records",
                icon=ft.Icons.MEDICAL_INFORMATION,
            ),
        ], spacing=10, wrap=True),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)