"""Patient dashboard overview."""

import flet as ft
from state import AppState

def PatientDashboard():
    """Main patient dashboard overview."""
    
    user = AppState.get_user()
    user_name = user['full_name'] if user else "Patient"
    
    # Stats cards
    def create_stat_card(title, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=40),
                    ft.Column([
                        ft.Text(title, size=14, color="outline"),
                        ft.Text(
                            str(value),
                            size=32,
                            weight="bold",
                            color=color,
                        ),
                    ], spacing=2, expand=True),
                ], spacing=15),
            ]),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
            expand=True,
        )
    
    # Quick action buttons
    def create_action_button(text, icon, route, color):
        return ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(icon, color="onPrimary"),
                ft.Text(text, color="onPrimary"),
            ], spacing=10),
            bgcolor=color,
            on_click=lambda e: e.page.go(route),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=15,
            ),
        )
    
    # Order list item
    def create_order_item(order_id, item_name, status, status_color):
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(f"Order {order_id}", weight="bold"),
                    ft.Text(item_name, size=12, color="outline"),
                ], spacing=2, expand=True),
                ft.Container(
                    content=ft.Text(status, size=12, weight="bold", color="onPrimaryContainer"),
                    bgcolor=ft.Colors.with_opacity(0.1, status_color),
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    border_radius=5,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=10,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
        )
    
    # Notification item
    def create_notification(message, time, icon, icon_color):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=icon_color, size=30),
                ft.Column([
                    ft.Text(message, size=13),
                    ft.Text(time, size=11, color="outline"),
                ], spacing=2, expand=True),
            ], spacing=10),
            padding=10,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
        )
    
    return ft.Column([
        # Welcome message
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.WAVING_HAND, color="tertiary", size=40),
                ft.Column([
                    ft.Text(
                        f"Welcome back, {user_name}!",
                        size=28,
                        weight="bold",
                    ),
                    ft.Text(
                        "Here's your health overview",
                        size=14,
                        color="outline",
                    ),
                ], spacing=5),
            ], spacing=15),
            padding=20,
        ),
        
        # Stats row
        ft.Row([
            create_stat_card("Active Prescriptions", "3", ft.Icons.MEDICATION, "primary"),
            create_stat_card("Pending Orders", "1", ft.Icons.PENDING_ACTIONS, "tertiary"),
            create_stat_card("Completed Orders", "12", ft.Icons.CHECK_CIRCLE, "primary"),
        ], spacing=15),
        
        ft.Container(height=20),
        
        # Quick actions
        ft.Container(
            content=ft.Column([
                ft.Text("Quick Actions", size=20, weight="bold"),
                ft.Row([
                    create_action_button("Browse Medicines", ft.Icons.SEARCH, "/patient/search", "primary"),
                    create_action_button("Upload Prescription", ft.Icons.UPLOAD_FILE, "/patient/prescriptions", "secondary"),
                    create_action_button("View Cart", ft.Icons.SHOPPING_CART, "/patient/cart", "tertiary"),
                ], spacing=15, wrap=True),
            ], spacing=15),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
        
        ft.Container(height=20),
        
        # Recent orders and notifications
        ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Recent Orders", size=20, weight="bold"),
                        ft.TextButton("View All →", on_click=lambda e: e.page.go("/patient/orders")),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    create_order_item("ORD-1234", "Paracetamol 500mg", "Ready", "primary"),
                    create_order_item("ORD-1233", "Amoxicillin 250mg", "Processing", "tertiary"),
                    create_order_item("ORD-1232", "Vitamin C 500mg", "Completed", "outline"),
                ], spacing=10),
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(1, "outlineVariant"),
                expand=2,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Notifications", size=20, weight="bold"),
                    ft.Divider(),
                    create_notification("Prescription ready for pickup", "2 hours ago", ft.Icons.MEDICATION, "primary"),
                    create_notification("New medicines available", "1 day ago", ft.Icons.NEW_RELEASES, "secondary"),
                ], spacing=10),
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(1, "outlineVariant"),
                expand=1,
            ),
        ], spacing=15),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)