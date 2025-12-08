"""User management - Add, Edit, Delete users with real database."""

import flet as ft
from services.database import get_db_connection
from services.auth import hash_password
from datetime import datetime

def UserManagement():
    """User management interface with full CRUD operations."""
    
    users_container = ft.Column(spacing=10)
    search_field = ft.TextField(
        hint_text="Search users...",
        prefix_icon=ft.Icons.SEARCH,
        border_color="outline",
        width=300,
    )
   
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
    )
    
    # Main container reference
    main_container = None
    
    def load_users(e=None):
        """Load users from database"""
        try:
            query = search_field.value.lower() if search_field.value else ""
            role = role_filter.value
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = "SELECT * FROM users WHERE 1=1"
            params = []
            
            if query:
                sql += " AND (LOWER(username) LIKE ? OR LOWER(full_name) LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])
            
            if role != "All":
                sql += " AND role = ?"
                params.append(role)
            
            sql += " ORDER BY created_at DESC"
            
            cursor.execute(sql, params)
            users = cursor.fetchall()
            conn.close()
            
            users_container.controls.clear()
            
            if users:
                # Table header
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
                
                # User rows
                for user in users:
                    users_container.controls.append(create_user_row(user, load_users, main_container))
            else:
                users_container.controls.append(
                    ft.Container(
                        content=ft.Text("No users found", size=16, color="outline"),
                        padding=50,
                        alignment=ft.alignment.center,
                    )
                )
            
            if main_container and main_container.page:
                main_container.page.update()
        except Exception as ex:
            print(f"Error loading users: {ex}")
            import traceback
            traceback.print_exc()
    
    def create_user_row(user, refresh_callback, container):
        """Create a row for displaying user information"""
        
        def delete_user(e):
            """Handle user deletion"""
            try:
                def confirm_delete(dialog_e):
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM users WHERE id = ?", (user['id'],))
                        conn.commit()
                        conn.close()
                        
                        e.page.close(dialog)
                        e.page.show_snack_bar(
                            ft.SnackBar(
                                content=ft.Text(f"User '{user['username']}' deleted successfully"),
                                bgcolor="green"
                            )
                        )
                        refresh_callback(e)
                    except Exception as ex:
                        print(f"Delete error: {ex}")
                        e.page.show_snack_bar(
                            ft.SnackBar(
                                content=ft.Text(f"Error: {str(ex)}"),
                                bgcolor="red"
                            )
                        )
                        e.page.update()
                
                def cancel_delete(dialog_e):
                    dialog_e.page.close(dialog)
                
                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Confirm Delete"),
                    content=ft.Text(f"Delete user '{user['username']}'?\nThis cannot be undone."),
                    actions=[
                        ft.TextButton("Cancel", on_click=cancel_delete),
                        ft.TextButton("Delete", on_click=confirm_delete),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                e.page.open(dialog)
            except Exception as ex:
                print(f"Error opening delete dialog: {ex}")
                import traceback
                traceback.print_exc()
        
        def edit_user(e):
            """Handle user editing"""
            try:
                username_field = ft.TextField(label="Username", value=user['username'], disabled=True)
                fullname_field = ft.TextField(label="Full Name", value=user['full_name'] or "")
                lastname_field = ft.TextField(label="Last Name", value=user['last_name'] or "")
                email_field = ft.TextField(label="Email", value=user['email'] or "")
                phone_field = ft.TextField(label="Phone", value=user['phone'] or "")
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
                    value=user['role']
                )
                password_field = ft.TextField(
                    label="New Password (optional)",
                    password=True,
                    can_reveal_password=True
                )
                
                def save_changes(dialog_e):
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        
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
                        dialog_e.page.show_snack_bar(
                            ft.SnackBar(
                                content=ft.Text("User updated successfully!"),
                                bgcolor="green"
                            )
                        )
                        refresh_callback(dialog_e)
                    except Exception as ex:
                        print(f"Save error: {ex}")
                        dialog_e.page.show_snack_bar(
                            ft.SnackBar(
                                content=ft.Text(f"Error: {str(ex)}"),
                                bgcolor="red"
                            )
                        )
                        dialog_e.page.update()
                
                def cancel_edit(dialog_e):
                    dialog_e.page.close(edit_dialog)
                
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
                        ft.TextButton("Cancel", on_click=cancel_edit),
                        ft.TextButton("Save", on_click=save_changes),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                
                e.page.open(edit_dialog)
            except Exception as ex:
                print(f"Error opening edit dialog: {ex}")
                import traceback
                traceback.print_exc()
        
        return ft.Container(
            content=ft.Row([
                ft.Text(user['username'], size=13, expand=1),
                ft.Text(user['full_name'] or "N/A", size=13, expand=2),
                ft.Container(
                    content=ft.Text(user['role'], size=11, weight="bold"),
                    bgcolor=ft.Colors.BLUE_100,
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border_radius=5,
                    expand=1,
                ),
                ft.Text(user['email'] or "N/A", size=13, expand=2),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        icon_color="blue",
                        tooltip="Edit User",
                        on_click=edit_user,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color="red",
                        tooltip="Delete User",
                        on_click=delete_user,
                    ),
                ], spacing=5, expand=1),
            ]),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
        )
    
    def add_user(e):
        """Show add user dialog"""
        try:
            username_field = ft.TextField(label="Username *", hint_text="Unique username")
            password_field = ft.TextField(label="Password *", password=True, can_reveal_password=True)
            fullname_field = ft.TextField(label="Full Name", hint_text="First name")
            lastname_field = ft.TextField(label="Last Name")
            email_field = ft.TextField(label="Email", hint_text="user@example.com")
            phone_field = ft.TextField(label="Phone", hint_text="09171234567")
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
                value="Patient"
            )
            
            def save_new_user(dialog_e):
                try:
                    if not username_field.value or not password_field.value:
                        dialog_e.page.show_snack_bar(
                            ft.SnackBar(
                                content=ft.Text("Username and password required!"),
                                bgcolor="red"
                            )
                        )
                        return
                    
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT id FROM users WHERE username = ?", (username_field.value,))
                    if cursor.fetchone():
                        conn.close()
                        dialog_e.page.show_snack_bar(
                            ft.SnackBar(
                                content=ft.Text("Username already exists!"),
                                bgcolor="red"
                            )
                        )
                        return
                    
                    cursor.execute("""
                        INSERT INTO users (username, password, role, full_name, last_name, email, phone, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (username_field.value, password_field.value, role_field.value, 
                          fullname_field.value, lastname_field.value, email_field.value, 
                          phone_field.value, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    
                    conn.commit()
                    conn.close()
                    
                    dialog_e.page.close(add_dialog)
                    dialog_e.page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text(f"User '{username_field.value}' created!"),
                            bgcolor="green"
                        )
                    )
                    load_users(dialog_e)
                except Exception as ex:
                    print(f"Save new user error: {ex}")
                    import traceback
                    traceback.print_exc()
                    dialog_e.page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text(f"Error: {str(ex)}"),
                            bgcolor="red"
                        )
                    )
            
            def cancel_add(dialog_e):
                dialog_e.page.close(add_dialog)
            
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
                    ft.TextButton("Cancel", on_click=cancel_add),
                    ft.TextButton("Create", on_click=save_new_user),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            e.page.open(add_dialog)
        except Exception as ex:
            print(f"Error opening add dialog: {ex}")
            import traceback
            traceback.print_exc()
    
    # Build main container
    main_container = ft.Column([
        ft.Row([
            ft.Text("User Management", size=28, weight="bold"),
        ]),
        ft.Text("Add, edit, and manage system users", size=14, color="grey"),
        
        ft.Container(height=20),
        
        ft.Row([
            search_field,
            role_filter,
            ft.ElevatedButton(
                "Search",
                icon=ft.Icons.SEARCH,
                on_click=load_users,
            ),
            ft.ElevatedButton(
                "Add User",
                icon=ft.Icons.ADD,
                on_click=add_user,
            ),
        ], spacing=10, wrap=True),
        
        ft.Container(height=20),
        
        users_container,
    ], scroll=ft.ScrollMode.AUTO, spacing=0)
    
    # Load users after a small delay to ensure page is ready
    def on_mount(e):
        load_users(e)
    
    main_container.on_mount = on_mount
    
    return main_container