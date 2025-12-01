import flet as ft
from database import init_db
#from database import initialize_database
from state import AppState

# Import Views
from ui.landing_page import LandingPage
from ui.login_page import LoginPage
from ui.app_layout import AppLayout

# Sub-views
# NEW:
from ui.patient import PatientDashboard, MedicineSearch, CartView, OrdersView, ProfileView
from ui.pharmacist_views import PharmacistDashboard, PrescriptionsView
from ui.inventory_views import InventoryDashboard, ManageStock
from ui.billing_views import BillingDashboard, InvoicesView
from ui.admin  import AdminDashboard, UserManagement, ReportsView, SystemLogs

def main(page: ft.Page):
    page.title = "Kaputt Kommandos PMS"
    page.window_width = 1024
    page.window_height = 768
    page.window_resizable = True 
    
    # Centers window on screen
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    try:
        page.window_center()
    except:
        pass 
    
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.TEAL)
    page.theme_mode = ft.ThemeMode.LIGHT 

    init_db()

    def route_change(route):
        page.views.clear()
        
        def create_view(route_path, controls, scroll_mode=ft.ScrollMode.AUTO):
            return ft.View(
                route_path,
                controls,
                padding=0,
                scroll=scroll_mode
            )

        troute = page.route

        # Show landing page
        if troute == "/":
            page.views.append(create_view("/", [LandingPage(page)], ft.ScrollMode.AUTO))
        
        # Show login page
        elif troute.startswith("/login"):
            try:
                role_param = troute.split("/")[2]
            except:
                role_param = "Patient"
            page.views.append(create_view(troute, [LoginPage(page, role_param)], ft.ScrollMode.AUTO))

        # Show dashboard if logged in
        else:
            user = AppState.get_user()
            if not user:
                page.go("/")
                return

            content = ft.Text("Not Found")
            
            if troute == "/dashboard":
                role = user['role']
                if role == "Patient": content = PatientDashboard()
                elif role == "Pharmacist": content = PharmacistDashboard()
                elif role == "Inventory": content = InventoryDashboard()
                elif role == "Billing": content = BillingDashboard()
                elif role == "Admin": content = AdminDashboard()
                else: content = ft.Text(f"Welcome {user['full_name']}")
            #content route for patient
            elif troute == "/patient/search": content = MedicineSearch()
            elif troute == "/patient/cart": content = CartView()
            elif troute == "/patient/orders": content = OrdersView()
            elif troute == "/patient/profile": content = ProfileView()

            elif troute == "/pharmacist/prescriptions": content = PrescriptionsView()
            elif troute == "/inventory/stock": content = ManageStock()
            elif troute == "/billing/invoices": content = InvoicesView()
            #content route for admin
            elif troute == "/admin/users": content = UserManagement()
            elif troute == "/admin/reports": content = ReportsView()
            elif troute == "/admin/logs": content = SystemLogs()

            page.views.append(create_view(troute, [AppLayout(page, content)], None))
        
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main)