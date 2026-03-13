import flet as ft
from state.app_state import AppState
from services.database import get_db_connection
from utils.notifications import show_success

# Render primary framework layout component
class AppLayout(ft.Row):
    def __init__(self, page: ft.Page, content_control):
        super().__init__()
        self.page = page
        self.expand = True 
        self.spacing = 0

        # Initialize interface theme toggle
        def toggle_theme(e):
            if self.page.theme_mode == ft.ThemeMode.LIGHT:
                self.page.theme_mode = ft.ThemeMode.DARK
                e.control.icon = ft.Icons.DARK_MODE
            else:
                self.page.theme_mode = ft.ThemeMode.LIGHT
                e.control.icon = ft.Icons.LIGHT_MODE
            self.page.update()

        # Contextualize application state
        user = AppState.get_user()
        user_name = user['full_name'] if user else "Guest"
        user_role = user['role'] if user else "Unknown"

        # Configure navigational rail view
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

        # Define traversal callbacks
        def go_back(e):
            """Navigate to previous view or landing page."""
            # Handle root dashboard navigation
            if self.page.route == "/dashboard":
                self.page.go("/")
            elif len(self.page.views) > 1:
                self.page.views.pop()
                # Update cart count before going back
                self.update_cart_count()
                self.page.go(self.page.views[-1].route)
            else:
                # Fallback navigation
                self.update_cart_count()
                self.page.go("/dashboard")
        
        def go_home(e):
            """Navigate to application dashboard."""
            self.update_cart_count()
            self.page.go("/dashboard")
        
        def refresh_page(e):
            """Refresh current view and update cart badge."""
            # Update cart count in sidebar before refreshing
            self.update_cart_count()
            current_route = self.page.route
            self.page.go(current_route)

        # Render application branding header
        self.top_bar = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            bgcolor="surface",
            border=ft.border.only(bottom=ft.border.BorderSide(1, "outlineVariant")),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    # System traversal buttons
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_size=24,
                        tooltip="Go Back",
                        on_click=go_back
                    ),
                    # Session identification component
                    ft.Column([
                        ft.Text(f"{user_name}", size=16, weight="bold"),
                        ft.Text(f"{user_role}", size=12, color="outline"),
                    ], spacing=2, expand=True),
                    # Render general purpose actions
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.HOME,
                            icon_size=24,
                            tooltip="Go to Dashboard",
                            on_click=go_home
                        ),
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            icon_size=24,
                            tooltip="Refresh Page",
                            on_click=refresh_page
                        ),
                        ft.IconButton(
                            ft.Icons.DARK_MODE,
                            icon_size=24,
                            tooltip="Toggle Theme",
                            on_click=toggle_theme
                        )
                    ], spacing=0)
                ]
            )
        )

        # Isolate main content execution context
        # Setup scrolling viewport
        self.scrollable_content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(content=content_control, expand=True, padding=20)
            ]
        )
        
        self.content_area = ft.Column(
            expand=True, 
            controls=[
                self.top_bar,  # Render sticky navigation bar
                self.scrollable_content  # Render dynamic content pane
            ],
            spacing=0
        )

        self.controls = [self.rail, ft.VerticalDivider(width=1), self.content_area]

    # Infer modular destinations per role authorizations
    def get_destinations(self):
        user = AppState.get_user()
        role = user['role']
        dests = [ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD, label="Dashboard")]
        
        if role == "Patient":
            # Execute metric aggregation for user view
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
            
            # Base navigation modules
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.SEARCH, label="Search Meds"))
            
            # Inject context into component attributes
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
        
        # Add persistent exit component
        if role != "Patient":
            dests.append(ft.NavigationRailDestination(icon=ft.Icons.LOGOUT, label="Logout"))
        
        return dests

    # Navigation rail dispatch mechanism
    def nav_change(self, e):
        index = e.control.selected_index
        label = e.control.destinations[index].label

        # Sanitize incoming item label metadata
        if "(" in label:
            label = label.split(" (")[0]

        if label == "Logout":
            confirm_dialog = None
            
            def confirm_logout_dialog(dialog_e):
                dialog_e.page.close(confirm_dialog)
                AppState.set_user(None)
                dialog_e.page.go("/")
            
            # Render system prompt dialog
            confirm_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.LOGOUT, color="error"),
                    ft.Text("Confirm Logout")
                ]),
                content=ft.Text("Are you sure you want to logout?", size=14),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda x: self.page.close(confirm_dialog)),
                    ft.ElevatedButton(
                        "Logout",
                        bgcolor="error",
                        color="white",
                        on_click=confirm_logout_dialog
                    ),
                ],
            )
            self.page.open(confirm_dialog) 
        elif label == "Dashboard": self.page.go("/dashboard")
        # Role-based redirect configurations
        elif label == "Search Meds": self.page.go("/patient/search")
        elif label == "My Cart": self.page.go("/patient/cart")
        elif label == "My Orders": self.page.go("/patient/orders")
        elif label == "My Bills": self.page.go("/patient/invoices")
        elif label == "My Profile": self.page.go("/patient/profile")
        # Staff modular views
        elif label == "Prescriptions": self.page.go("/pharmacist/prescriptions")
        elif label == "Manage Stock": self.page.go("/inventory/stock")
        elif label == "Invoices": self.page.go("/billing/invoices")
        elif label == "Find Patient": self.page.go("/staff/search")
        elif label == "All Patients": self.page.go("/staff/patients")
        elif label == "Help Desk": self.page.go("/staff/help")
        # System administrative views
        elif label == "Users": self.page.go("/admin/users")
        elif label == "Reports": self.page.go("/admin/reports")
        elif label == "Logs": self.page.go("/admin/logs")

    # Badge synchronization hook
    def update_cart_count(self):
        """Refresh the cart count in the sidebar for Patient roles"""
        user = AppState.get_user()
        if user and user['role'] == "Patient":
            try:
                cart_count = 0
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(quantity) FROM cart WHERE patient_id = ?", (user['id'],))
                res = cursor.fetchone()
                if res and res[0]:
                    cart_count = res[0]
                conn.close()
                
                # Update the cart label in the rail destinations
                for i, dest in enumerate(self.rail.destinations):
                    if "My Cart" in dest.label:
                        cart_label = f"My Cart ({cart_count})" if cart_count > 0 else "My Cart"
                        # Update the destination label
                        self.rail.destinations[i] = ft.NavigationRailDestination(
                            icon=ft.Icons.SHOPPING_CART, 
                            label=cart_label
                        )
                        self.page.update()
                        break
            except:
                pass