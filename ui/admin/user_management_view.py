"""User management - Add, Edit, Delete, Deactivate users."""

import flet as ft
from database import get_db_connection

def UserManagement():
    """User management interface."""
    
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
    
    def load_users(e=None):
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
                users_container.controls.append(create_user_row(user, load_users))
        else:
            users_container.controls.append(
                ft.Container(
                    content=ft.Text("No users found", size=16, color="outline"),
                    padding=50,
                    alignment=ft.alignment.center,
                )
            )
        
        if e:
            e.page.update()
    
    def create_user_row(user, refresh_callback):
        def delete_user(e):
            # Show confirmation dialog
            def confirm_delete(dialog_e):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id = ?", (user['id'],))
                conn.commit()
                conn.close()
                
                dialog.open = False
                e.page.update()
                refresh_callback(e)
            
            def cancel_delete(dialog_e):
                dialog.open = False
                e.page.update()
            
            dialog = ft.AlertDialog(
                title=ft.Text("Confirm Delete"),
                content=ft.Text(f"Are you sure you want to delete user '{user['username']}'?"),
                actions=[
                    ft.TextButton("Cancel", on_click=cancel_delete),
                    ft.ElevatedButton("Delete", bgcolor="error", color="onError", on_click=confirm_delete),
                ],
            )
            e.page.dialog = dialog
            dialog.open = True
            e.page.update()
        
        def edit_user(e):
            e.page.snack_bar = ft.SnackBar(content=ft.Text("Edit feature coming soon!"))
            e.page.snack_bar.open = True
            e.page.update()
        
        return ft.Container(
            content=ft.Row([
                ft.Text(user['username'], size=13, expand=1),
                ft.Text(user['full_name'], size=13, expand=2),
                ft.Container(
                    content=ft.Text(user['role'], size=11, weight="bold", color="onPrimaryContainer"),
                    bgcolor=ft.Colors.with_opacity(0.2, "primary"),
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
            bgcolor="surface",
        )
    
    # Initial load
    class FakePage:
        dialog = None
        snack_bar = None
        def update(self): pass
    load_users(type('Event', (), {'page': FakePage()})())
    
    return ft.Column([
        ft.Row([
            ft.Text("User Management", size=28, weight="bold"),
        ]),
        ft.Text("Add, edit, and manage system users", size=14, color="outline"),
        
        ft.Container(height=20),
        
        # Search and filters
        ft.Row([
            search_field,
            role_filter,
            ft.ElevatedButton(
                "Search",
                icon=ft.Icons.SEARCH,
                on_click=load_users,
                bgcolor="primary",
                color="onPrimary",
            ),
            ft.ElevatedButton(
                "Add User",
                icon=ft.Icons.ADD,
                bgcolor="secondary",
                color="onSecondary",
            ),
        ], spacing=10, wrap=True),
        
        ft.Container(height=20),
        
        # Users list
        users_container,
    ], scroll=ft.ScrollMode.AUTO, spacing=0)