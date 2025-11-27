import flet as ft

def LandingPage(page: ft.Page):
    
    # Go to the login page for the role clicked
    def select_role(role_name):
        page.go(f"/login/{role_name}")

    # Switch between dark and light mode
    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        e.control.icon = ft.Icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE
        page.update()

    # Helper to make the little role cards
    def create_role_card(icon, label, role_key):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=45, color="primary"),
                ft.Text(label, weight="bold", size=13, text_align="center", color="onSurfaceVariant"),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=160, 
            height=130,
            bgcolor="surfaceVariant",
            border_radius=12,
            padding=10,
            ink=True, # Makes it ripple when clicked
            on_click=lambda _: select_role(role_key),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=5,
                color=ft.Colors.with_opacity(0.1, ft.Colors.SHADOW),
                offset=ft.Offset(2, 2)
            ),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, "outline")) 
        )

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=0,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            # Header with the logo and green background
            ft.Container(
                width=float("inf"),
                height=250,
                bgcolor="primary",
                padding=20,
                alignment=ft.alignment.center,
                content=ft.Stack([
                    # Center text
                    ft.Container(
                        alignment=ft.alignment.center,
                        content=ft.Column([
                            ft.Icon(name=ft.Icons.LOCAL_PHARMACY, size=70, color="onPrimary"),
                            ft.Text("Kaputt Kommando's", size=36, weight="bold", color="onPrimary", text_align="center"),
                            ft.Text("Pharmacy Management System", size=18, color="onPrimaryContainer", weight="w500", text_align="center"),
                            ft.Text("Today Health is Caring • For Future Start With Your Health", size=12, italic=True, color="onPrimary", text_align="center"),
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    ),
                    # Theme button top right
                    ft.Container(
                        alignment=ft.alignment.top_right,
                        content=ft.IconButton(ft.Icons.DARK_MODE, on_click=toggle_theme, icon_color="onPrimary", tooltip="Toggle Theme")
                    )
                ])
            ),

            ft.Container(height=40),
            ft.Text("Select your Role to Login", size=22, weight="bold", color="onSurface"),
            ft.Container(height=20),

            # The grid of role buttons (3 top, 3 bottom)
            ft.Column(
                spacing=20,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                        controls=[
                            create_role_card(ft.Icons.PERSON_ADD, "Patient", "Patient"), 
                            create_role_card(ft.Icons.ADMIN_PANEL_SETTINGS, "Administrator", "Admin"),
                            create_role_card(ft.Icons.MEDICAL_SERVICES, "Pharmacist", "Pharmacist"),
                        ]
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                        controls=[
                            create_role_card(ft.Icons.INVENTORY, "Inventory Manager", "Inventory"),
                            create_role_card(ft.Icons.RECEIPT_LONG, "Billing Clerk", "Billing"),
                            create_role_card(ft.Icons.BADGE, "Staff Member", "Staff"),
                        ]
                    )
                ]
            ),
            
            ft.Container(height=50),
            ft.Text("Group 5: Colico | David | Nonato", size=11, color="outline"),
            ft.Container(height=20),
        ]
    )