import flet as ft
from state import AppState

# This class handles the sidebar and the top bar for the main app
class AppLayout(ft.Row):
    def __init__(self, page: ft.Page, content_control):
        super().__init__()
        self.page = page
        self.expand = True 
        self.spacing = 0

        # Switches between light and dark mode
        def toggle_theme(e):
            if self.page.theme_mode == ft.ThemeMode.LIGHT:
                self.page.theme_mode = ft.ThemeMode.DARK
                e.control.icon = ft.Icons.DARK_MODE
            else:
                self.page.theme_mode = ft.ThemeMode.LIGHT
                e.control.icon = ft.Icons.LIGHT_MODE
            self.page.update()

        # Get the current user info to show on top
        user = AppState.get_user()
        user_name = user['full_name'] if user else "Guest"
        user_role = user['role'] if user else "Unknown"

        # The sidebar menu
        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=self.get_destinations(),
            on_change=self.nav_change,
            bgcolor="surfaceVariant",
        )

        # The top header bar
        self.top_bar = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            bgcolor="surface",
            border=ft.border.only(bottom=ft.border.BorderSide(1, "outlineVariant")),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column([
                        ft.Text(f"{user_name}", size=16, weight="bold"),
                        ft.Text(f"{user_role}", size=12, color="outline"),
                    ], spacing=2),
                    ft.IconButton(ft.Icons.DARK_MODE, on_click=toggle_theme)
                ]
            )
        )

        # The main area where page content goes
        self.content_area = ft.Column(
            expand=True, 
            controls=[
                self.top_bar,
                ft.Container(
                    content=content_control, 
                    expand=True, 
                    padding=20,
                    
                )
            ],
            scroll=ft.ScrollMode.AUTO
        )

        self.controls = [self.rail, ft.VerticalDivider(width=1), self.content_area]

    # Figures out which buttons to show based on who is logged in
    def get_destinations(self):
        role = AppState.get_user()['role']
        dests = [ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD, label="Dashboard")]
        if role == "Patient":
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.SEARCH, label="Search Meds"))
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.SHOPPING_CART, label="My Cart"))
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.RECEIPT_LONG, label="My Orders"))
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.PERSON, label="My Profile")) 
        elif role == "Pharmacist":
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.MEDICAL_SERVICES, label="Prescriptions"))
        elif role == "Inventory":
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.INVENTORY, label="Manage Stock"))
        elif role == "Billing":
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.RECEIPT_LONG, label="Invoices"))
        elif role == "Admin":
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.PEOPLE, label="Users"))
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.LOGOUT, label="Logout"))
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.ANALYTICS, label="Reports"))
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.HISTORY, label="Logs"))
        return dests

    # Handles clicking the sidebar buttons
    def nav_change(self, e):
        index = e.control.selected_index
        label = e.control.destinations[index].label
        
        if label == "Logout":
            AppState.set_user(None)
            self.page.go("/") 
        #For patient
        elif label == "Dashboard": self.page.go("/dashboard")
        elif label == "Search Meds": self.page.go("/patient/search")
        elif label == "My Cart": self.page.go("/patient/cart")
        elif label == "My Orders": self.page.go("/patient/orders")
        elif label == "My Profile": self.page.go("/patient/profile")

        elif label == "Prescriptions": self.page.go("/pharmacist/prescriptions")
        elif label == "Manage Stock": self.page.go("/inventory/stock")
        elif label == "Invoices": self.page.go("/billing/invoices")
        #For admin
        elif label == "Users": self.page.go("/admin/users")
        elif label == "Reports": self.page.go("/admin/reports")
        elif label == "Logs": self.page.go("/admin/logs")