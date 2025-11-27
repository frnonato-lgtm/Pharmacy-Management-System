"""Admin portal package."""
#Subview import for admin
from ui.admin.admin_views import AdminDashboard
from ui.admin.user_management_view import UserManagement
from ui.admin.reports_view import ReportsView
from ui.admin.system_logs_view import SystemLogs

__all__ = ['AdminDashboard', 'UserManagement', 'ReportsView', 'SystemLogs']