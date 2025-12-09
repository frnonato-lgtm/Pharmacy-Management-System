import flet as ft
from state.app_state import AppState
from services.database import get_db_connection

# This handles the Sidebar layout and the Top Header
class AppLayout(ft.Row):
    def __init__(self, page: ft.Page, content_control):
        super().__init__()
        self.page = page
        self.expand = True 
        self.spacing = 0

        # Dark mode toggle button logic
        def toggle_theme(e):
            if self.page.theme_mode == ft.ThemeMode.LIGHT:
                self.page.theme_mode = ft.ThemeMode.DARK
                e.control.icon = ft.Icons.DARK_MODE
            else:
                self.page.theme_mode = ft.ThemeMode.LIGHT
                e.control.icon = ft.Icons.LIGHT_MODE
            self.page.update()

        # Get current user info for the header
        user = AppState.get_user()
        user_name = user['full_name'] if user else "Guest"
        user_role = user['role'] if user else "Unknown"

        # Sidebar navigation menu
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

        # Top Header Bar
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

        # Main Content Area (where the pages load)
        self.content_area = ft.Column(
            expand=True, 
            controls=[
                self.top_bar,
                ft.Container(content=content_control, expand=True, padding=20)
            ],
            scroll=ft.ScrollMode.AUTO
        )

        self.controls = [self.rail, ft.VerticalDivider(width=1), self.content_area]

    # Decide which buttons to show based on the user's role
    def get_destinations(self):
        user = AppState.get_user()
        role = user['role']
        dests = [ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD, label="Dashboard")]
        
        if role == "Patient":
            # --- GET CART COUNT ---
            cart_count = 0
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(quantity) FROM cart WHERE patient_id = ?", (user['id'],))
                res = cursor.fetchone()
                if res and res[0]:
                    cart_count = res[0]
                conn.close()
            except:
                pass
            
            # Standard Icon to prevent crash
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.SEARCH, label="Search Meds"))
            
            # Show count in label instead of badge to fix error
            cart_label = f"My Cart ({cart_count})" if cart_count > 0 else "My Cart"
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.SHOPPING_CART, label=cart_label))
            
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.RECEIPT_LONG, label="My Orders"))
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.RECEIPT_LONG, label="My Bills")) 
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.PERSON, label="My Profile")) 
            
        elif role == "Pharmacist":
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.MEDICAL_SERVICES, label="Prescriptions"))
        elif role == "Inventory":
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.INVENTORY, label="Manage Stock"))
        elif role == "Billing":
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.RECEIPT_LONG, label="Invoices"))
        elif role == "Admin":
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.PEOPLE, label="Users"))
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.ANALYTICS, label="Reports"))
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.HISTORY, label="Logs"))
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.INVENTORY, label="Manage Stock"))
        elif role == "Staff":
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.PERSON_SEARCH, label="Find Patient"))
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.PEOPLE, label="All Patients"))  
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.HELP, label="Help Desk"))  
        
        # Only show Logout in sidebar if NOT a Patient
        if role != "Patient":
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.LOGOUT, label="Logout"))
        
        return dests

    # Handle clicks on the sidebar
    def nav_change(self, e):
        index = e.control.selected_index
        label = e.control.destinations[index].label
        
        # Clean label if it has numbers (e.g. "My Cart (2)" -> "My Cart")
        if "(" in label:
            label = label.split(" (")[0]

        if label == "Logout":
            AppState.set_user(None)
            self.page.go("/") 
        elif label == "Dashboard": self.page.go("/dashboard")
        # Patient links
        elif label == "Search Meds": self.page.go("/patient/search")
        elif label == "My Cart": self.page.go("/patient/cart")
        elif label == "My Orders": self.page.go("/patient/orders")
        elif label == "My Bills": self.page.go("/patient/invoices")
        elif label == "My Profile": self.page.go("/patient/profile")
        # Staff links
        elif label == "Prescriptions": self.page.go("/pharmacist/prescriptions")
        elif label == "Manage Stock": self.page.go("/inventory/stock")
        elif label == "Invoices": self.page.go("/billing/invoices")
        elif label == "Find Patient": self.page.go("/staff/search")
        elif label == "All Patients": self.page.go("/staff/patients")
        elif label == "Help Desk": self.page.go("/staff/help")
        # Admin links
        elif label == "Users": self.page.go("/admin/users")
        elif label == "Reports": self.page.go("/admin/reports")
        elif label == "Logs": self.page.go("/admin/logs")