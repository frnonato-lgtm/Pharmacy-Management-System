import flet as ft
from services.database import init_db
from state.app_state import AppState

# Import Main Views
from views.landing_page import LandingPage
from views.login_page import LoginPage
from components.app_layout import AppLayout

# Import Role-Specific Views
from views.patient.patient_dashboard import PatientDashboard
from views.patient.medicine_search import MedicineSearch
from views.patient.cart_view import CartView
from views.patient.orders_view import OrdersView
from views.patient.profile_view import ProfileView

from views.admin.admin_dashboard import AdminDashboard
from views.admin.user_management import UserManagement
from views.admin.reports_view import ReportsView as AdminReportsView
from views.admin.logs_view import SystemLogs
#from views.audit_log_viewer import AuditLogViewer

from views.inventory.inventory_dashboard import InventoryDashboard
from views.inventory.manage_stock import ManageStock

from views.pharmacist.pharmacist_dashboard import PharmacistDashboard
from views.pharmacist.prescriptions_view import PrescriptionsView
from views.pharmacist.prescription_detail import PrescriptionDetailView  
from views.pharmacist.reports_view import ReportsView as PharmacistReportsView  
from views.pharmacist.medicine_search import PharmacistMedicineSearch

from views.billing.billing_dashboard import BillingDashboard
from views.billing.create_invoices_view import CreateInvoicesView
from views.billing.billing_reports_view import BillingReportsView
from views.billing.invoices_list_view import InvoicesListView
from views.billing.payment_history_view import PaymentHistoryView

from views.staff.staff_dashboard import StaffDashboard
from views.staff.patient_search import StaffPatientSearch
from views.staff.patient_detail import StaffPatientDetail
from views.staff.all_patients import AllPatientsView
from views.staff.help_desk import HelpDeskView

def main(page: ft.Page):
    page.title = "Kaputt Kommandos PMS"
    page.window_width = 1024
    page.window_height = 768
    page.window_resizable = True 
    
    # Center the app
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    try: page.window_center()
    except: pass 
    
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.TEAL)
    page.theme_mode = ft.ThemeMode.LIGHT 

    # Start the DB
    init_db()

    def route_change(route):
        page.views.clear()
        
        # Helper to simplify view creation
        def create_view(route_path, controls, scroll_mode=ft.ScrollMode.AUTO):
            return ft.View(route_path, controls, padding=0, scroll=scroll_mode)

        troute = page.route

        # Landing
        if troute == "/":
            page.views.append(create_view("/", [LandingPage(page)], ft.ScrollMode.AUTO))
        
        # Login
        elif troute.startswith("/login"):
            try: role_param = troute.split("/")[2]
            except: role_param = "Patient"
            page.views.append(create_view(troute, [LoginPage(page, role_param)], ft.ScrollMode.AUTO))

        # Dashboard / Protected Routes
        else:
            user = AppState.get_user()
            if not user:
                page.go("/")
                return

            content = ft.Text("Not Found")
            
            # 1. Dashboards
            if troute == "/dashboard":
                role = user['role']
                if role == "Patient": content = PatientDashboard()
                elif role == "Pharmacist": content = PharmacistDashboard()
                elif role == "Inventory": content = InventoryDashboard()
                elif role == "Billing": content = BillingDashboard()
                elif role == "Admin": content = AdminDashboard()
                elif role == "Staff": content = StaffDashboard()
                else: content = ft.Text(f"Welcome {user['full_name']}")

            # 2. Patient Views
            elif troute == "/patient/search": content = MedicineSearch()
            elif troute == "/patient/cart": content = CartView()
            elif troute == "/patient/orders": content = OrdersView()
            elif troute == "/patient/profile": content = ProfileView()

            # 3. Pharmacist Views
            elif troute == "/pharmacist/prescriptions": content = PrescriptionsView()
            elif troute == "/pharmacist/reports": content = PharmacistReportsView() 
            elif troute == "/pharmacist/medicines": content = PharmacistMedicineSearch()
            elif troute.startswith("/pharmacist/prescription/"):
                rx_id = troute.split("/")[-1]
                try:
                    rx_id = int(rx_id)
                    content = PrescriptionDetailView(rx_id)
                except (ValueError, IndexError):
                    # Invalid prescription ID, redirect to list
                    page.go("/pharmacist/prescriptions")
                    return

            # 4. Inventory Views
            elif troute == "/inventory/stock": content = ManageStock()

            # 5. Billing Views
            elif troute == "/billing/create-invoice": content = CreateInvoicesView()
            elif troute == "/billing/invoices": content = InvoicesListView()
            elif troute == "/billing/payments": content = PaymentHistoryView()
            elif troute == "/billing/reports" : content = BillingReportsView()
            # 6. Admin Views
            elif troute == "/admin/users": content = UserManagement()
            elif troute == "/admin/reports": content = AdminReportsView()
            elif troute == "/admin/logs": content = SystemLogs()
            #elif troute == "/admin/audit": content = AuditLogViewer()
            # 7. Staff Views
            elif troute == "/staff/search": content = StaffPatientSearch()
            #elif troute == "/staff/patients": content = StaffPatientDetail()
            elif troute == "/staff/patients": content = AllPatientsView() 
            elif troute == "/staff/help": content = HelpDeskView()
            elif troute.startswith("/staff/patient/"):
                patient_id = troute.split("/")[-1]
                content = StaffPatientDetail(patient_id)
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