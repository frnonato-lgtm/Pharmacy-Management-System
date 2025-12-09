"""User management - Add, Edit, Delete users with real database."""

import flet as ft
from services.database import get_db_connection
from datetime import datetime

def UserManagement():
    """User management interface with full CRUD operations."""
    
    # This list holds all the user cards
    users_container = ft.Column(spacing=10)
    
    # Search box to find users
    search_field = ft.TextField(
        hint_text="Search users...",
        prefix_icon=ft.Icons.SEARCH,
        border_color="primary", # Added color so it shows in dark mode
        width=300,
    )
   
    # Dropdown to filter by role (Admin, Patient, etc.)
    role_filter = ft.Dropdown(
        label="Filter by Role",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Patient"),
            ft.dropdown.Option("Pharmacist"),
            ft.dropdown.Option("Inventory"),
            ft.dropdown.Option("Billing"),
            ft.dropdown.Option("Staff"),
            ft.dropdown.Option("Admin"),
        ],
        value="All",
        width=200,
        border_color="primary", # Fix for dark mode visibility
    )
    
    # This function loads the users from the database
    def load_users(e=None):
        try:
            # Get values from the search box and dropdown
            query = search_field.value.lower() if search_field.value else ""
            role = role_filter.value
            
            # Connect to database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Base query
            sql = "SELECT * FROM users WHERE 1=1"
            params = []
            
            # Add search condition if typed
            if query:
                sql += " AND (LOWER(username) LIKE ? OR LOWER(full_name) LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])
            
            # Add role filter if selected
            if role != "All":
                sql += " AND role = ?"
                params.append(role)
            
            # Sort by newest first
            sql += " ORDER BY created_at DESC"
            
            cursor.execute(sql, params)
            users = cursor.fetchall()
            conn.close()
            
            # Clear the current list
            users_container.controls.clear()
            
            if users:
                # Add the table header
                users_container.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Username", size=13, weight="bold", expand=1),
                            ft.Text("Full Name", size=13, weight="bold", expand=2),
                            ft.Text("Role", size=13, weight="bold", expand=1),
                            ft.Text("Email", size=13, weight="bold", expand=2),
                            ft.Text("Actions", size=13, weight="bold", expand=1),
                        ]),
                        bgcolor="surfaceVariant",
                        padding=15,
                        border_radius=8,
                    )
                )
                
                # Loop through users and add rows
                for user in users:
                    users_container.controls.append(create_user_row(user, load_users))
            else:
                # Show message if no users found
                users_container.controls.append(
                    ft.Container(
                        content=ft.Text("No users found", size=16, color="outline"),
                        padding=50,
                        alignment=ft.alignment.center,
                    )
                )
            
            if e: e.page.update()
            
        except Exception as ex:
            print(f"Error loading users: {ex}")
    
    # Helper to create a single row for a user
    def create_user_row(user, refresh_callback):
        
        # Function to delete a user
        def delete_user(e):
            def confirm_delete(dialog_e):
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM users WHERE id = ?", (user['id'],))
                    conn.commit()
                    conn.close()
                    
                    e.page.close(dialog)
                    e.page.snack_bar = ft.SnackBar(content=ft.Text(f"User '{user['username']}' deleted successfully"), bgcolor="primary")
                    e.page.snack_bar.open = True
                    e.page.update()
                    refresh_callback(e)
                except Exception as ex:
                    print(f"Delete error: {ex}")
            
            # Popup dialog to confirm
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirm Delete"),
                content=ft.Text(f"Delete user '{user['username']}'?\nThis cannot be undone."),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: e.page.close(dialog)),
                    ft.TextButton("Delete", on_click=confirm_delete),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            e.page.open(dialog)
        
        # Function to edit a user
        def edit_user(e):
            # Create text fields pre-filled with data
            # Added border_color="primary" to all for Dark Mode fix
            username_field = ft.TextField(label="Username", value=user['username'], disabled=True, border_color="primary")
            fullname_field = ft.TextField(label="Full Name", value=user['full_name'] or "", border_color="primary")
            lastname_field = ft.TextField(label="Last Name", value=user['last_name'] or "", border_color="primary")
            email_field = ft.TextField(label="Email", value=user['email'] or "", border_color="primary")
            phone_field = ft.TextField(label="Phone", value=user['phone'] or "", border_color="primary")
            
            role_field = ft.Dropdown(
                label="Role",
                options=[
                    ft.dropdown.Option("Patient"),
                    ft.dropdown.Option("Pharmacist"),
                    ft.dropdown.Option("Inventory"),
                    ft.dropdown.Option("Billing"),
                    ft.dropdown.Option("Staff"),
                    ft.dropdown.Option("Admin"),
                ],
                value=user['role'],
                border_color="primary"
            )
            
            password_field = ft.TextField(
                label="New Password (optional)",
                password=True,
                can_reveal_password=True,
                border_color="primary"
            )
            
            # Save function inside the edit dialog
            def save_changes(dialog_e):
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # If password field has text, update password too
                    if password_field.value:
                        cursor.execute("""
                            UPDATE users 
                            SET full_name=?, last_name=?, email=?, phone=?, role=?, password=?
                            WHERE id=?
                        """, (fullname_field.value, lastname_field.value, email_field.value, 
                              phone_field.value, role_field.value, password_field.value, user['id']))
                    else:
                        cursor.execute("""
                            UPDATE users 
                            SET full_name=?, last_name=?, email=?, phone=?, role=?
                            WHERE id=?
                        """, (fullname_field.value, lastname_field.value, email_field.value, 
                              phone_field.value, role_field.value, user['id']))
                    
                    conn.commit()
                    conn.close()
                    
                    dialog_e.page.close(edit_dialog)
                    dialog_e.page.snack_bar = ft.SnackBar(content=ft.Text("User updated successfully!"), bgcolor="primary")
                    dialog_e.page.snack_bar.open = True
                    dialog_e.page.update()
                    refresh_callback(dialog_e)
                except Exception as ex:
                    print(f"Save error: {ex}")

            # The actual edit popup
            edit_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(f"Edit User: {user['username']}"),
                content=ft.Container(
                    content=ft.Column([
                        username_field,
                        fullname_field,
                        lastname_field,
                        email_field,
                        phone_field,
                        role_field,
                        password_field,
                    ], tight=True, scroll=ft.ScrollMode.AUTO),
                    width=400,
                    height=400,
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: e.page.close(edit_dialog)),
                    ft.TextButton("Save", on_click=save_changes),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            e.page.open(edit_dialog)
        
        # Return the row UI
        return ft.Container(
            content=ft.Row([
                ft.Text(user['username'], size=13, expand=1),
                ft.Text(user['full_name'] or "N/A", size=13, expand=2),
                ft.Container(
                    content=ft.Text(user['role'], size=11, weight="bold", color="onPrimaryContainer"),
                    bgcolor="primaryContainer",
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border_radius=5,
                    expand=1,
                ),
                ft.Text(user['email'] or "N/A", size=13, expand=2),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        icon_color="primary",
                        tooltip="Edit User",
                        on_click=edit_user,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color="error",
                        tooltip="Delete User",
                        on_click=delete_user,
                    ),
                ], spacing=5, expand=1),
            ]),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
            bgcolor="surface", # Dark mode fix
        )
    
    # Function to add a new user
    def add_user(e):
        # Create fields for new user
        # Added border_color="primary" for visibility
        username_field = ft.TextField(label="Username *", hint_text="Unique username", border_color="primary")
        password_field = ft.TextField(label="Password *", password=True, can_reveal_password=True, border_color="primary")
        fullname_field = ft.TextField(label="Full Name", hint_text="First name", border_color="primary")
        lastname_field = ft.TextField(label="Last Name", border_color="primary")
        email_field = ft.TextField(label="Email", hint_text="user@example.com", border_color="primary")
        phone_field = ft.TextField(label="Phone", hint_text="09171234567", border_color="primary")
        
        role_field = ft.Dropdown(
            label="Role *",
            options=[
                ft.dropdown.Option("Patient"),
                ft.dropdown.Option("Pharmacist"),
                ft.dropdown.Option("Inventory"),
                ft.dropdown.Option("Billing"),
                ft.dropdown.Option("Staff"),
                ft.dropdown.Option("Admin"),
            ],
            value="Patient",
            border_color="primary"
        )
        
        def save_new_user(dialog_e):
            try:
                # Check required fields
                if not username_field.value or not password_field.value:
                    dialog_e.page.snack_bar = ft.SnackBar(content=ft.Text("Username and password required!"), bgcolor="error")
                    dialog_e.page.snack_bar.open = True
                    dialog_e.page.update()
                    return
                
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Check for duplicates
                cursor.execute("SELECT id FROM users WHERE username = ?", (username_field.value,))
                if cursor.fetchone():
                    conn.close()
                    dialog_e.page.snack_bar = ft.SnackBar(content=ft.Text("Username already exists!"), bgcolor="error")
                    dialog_e.page.snack_bar.open = True
                    dialog_e.page.update()
                    return
                
                # Insert new user
                cursor.execute("""
                    INSERT INTO users (username, password, role, full_name, last_name, email, phone, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (username_field.value, password_field.value, role_field.value, 
                      fullname_field.value, lastname_field.value, email_field.value, 
                      phone_field.value, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
                conn.commit()
                conn.close()
                
                dialog_e.page.close(add_dialog)
                dialog_e.page.snack_bar = ft.SnackBar(content=ft.Text(f"User '{username_field.value}' created!"), bgcolor="primary")
                dialog_e.page.snack_bar.open = True
                dialog_e.page.update()
                load_users(dialog_e) # Refresh list
            except Exception as ex:
                print(f"Save new user error: {ex}")
        
        # The Add User popup
        add_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add New User"),
            content=ft.Container(
                content=ft.Column([
                    username_field,
                    password_field,
                    fullname_field,
                    lastname_field,
                    email_field,
                    phone_field,
                    role_field,
                ], tight=True, scroll=ft.ScrollMode.AUTO),
                width=400,
                height=400,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: e.page.close(add_dialog)),
                ft.TextButton("Create", on_click=save_new_user),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        e.page.open(add_dialog)
    
    # Trick to load users when the page starts
    class Fake: page=None
    load_users(type('E',(),{'page':Fake})())
    
    # --- PAGE LAYOUT ---
    return ft.Column([
        ft.Row([
            ft.Text("User Management", size=28, weight="bold"),
        ]),
        ft.Text("Add, edit, and manage system users", size=14, color="grey"),
        
        ft.Container(height=20),
        
        # Filter buttons row
        ft.Row([
            search_field,
            role_filter,
            ft.ElevatedButton(
                "Search",
                icon=ft.Icons.SEARCH,
                bgcolor="primary", # Added color
                color="white",
                on_click=load_users,
            ),
            ft.ElevatedButton(
                "Add User",
                icon=ft.Icons.ADD,
                bgcolor="secondary", # Added color
                color="white",
                on_click=add_user,
            ),
        ], spacing=10, wrap=True),
        
        ft.Container(height=20),
        
        # The list of users
        users_container,
    ], scroll=ft.ScrollMode.AUTO, spacing=0)