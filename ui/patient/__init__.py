"""Patient portal package."""
#Subview import for patient
from ui.patient.dashboard_view import PatientDashboard
from ui.patient.search_medicine_view import MedicineSearch
from ui.patient.cart_view import CartView
from ui.patient.orders_view import OrdersView
from ui.patient.profile_view import ProfileView

__all__ = ['PatientDashboard', 'MedicineSearch', 'CartView', 'OrdersView', 'ProfileView']