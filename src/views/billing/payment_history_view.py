"""Payment history view with transaction tracking."""

import flet as ft
from datetime import datetime, timedelta
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader

def PaymentHistoryView():
    """View all payment transactions and history."""
    
    payments_container = ft.Column(spacing=10)
    
    # Filter controls
    payment_method_filter = ft.Dropdown(
        label="Payment Method",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Cash"),
            ft.dropdown.Option("Credit Card"),
            ft.dropdown.Option("Debit Card"),
            ft.dropdown.Option("Bank Transfer"),
            ft.dropdown.Option("GCash"),
            ft.dropdown.Option("PayMaya"),
        ],
        value="All",
        width=180,
    )
    
    date_from = ft.TextField(
        label="From Date",
        value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        width=150,
        border_color="outline",
    )
    
    date_to = ft.TextField(
        label="To Date",
        value=datetime.now().strftime("%Y-%m-%d"),
        width=150,
        border_color="outline",
    )
    
    search_field = ft.TextField(
        hint_text="Search by invoice #, patient name...",
        prefix_icon=ft.Icons.SEARCH,
        border_color="outline",
        expand=True,
    )
    
    def get_payments_from_db(payment_method="All", date_start="", date_end="", search=""):
        """Get payment transactions from database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT i.id, i.invoice_number, i.total_amount, i.payment_method,
                   i.payment_date, i.created_at,
                   u.full_name as patient_name,
                   clerk.full_name as clerk_name
            FROM invoices i
            LEFT JOIN users u ON i.patient_id = u.id
            LEFT JOIN users clerk ON i.billing_clerk_id = clerk.id
            WHERE i.status = 'Paid'
        """
        
        params = []
        
        # Payment method filter
        if payment_method != "All":
            query += " AND i.payment_method = ?"
            params.append(payment_method)
        
        # Date range filter
        if date_start:
            query += " AND DATE(i.payment_date) >= ?"
            params.append(date_start)
        
        if date_end:
            query += " AND DATE(i.payment_date) <= ?"
            params.append(date_end)
        
        # Search filter
        if search:
            query += " AND (i.invoice_number LIKE ? OR u.full_name LIKE ?)"
            params.append(f"%{search}%")
            params.append(f"%{search}%")
        
        query += " ORDER BY i.payment_date DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def create_payment_card(payment):
        """Create payment transaction card."""
        inv_id, inv_number, amount, payment_method, payment_date, created_at, patient_name, clerk_name = payment
        
        # Payment method icons
        payment_icons = {
            'Cash': ft.Icons.MONEY,
            'Credit Card': ft.Icons.CREDIT_CARD,
            'Debit Card': ft.Icons.CREDIT_CARD,
            'Bank Transfer': ft.Icons.ACCOUNT_BALANCE,
            'GCash': ft.Icons.PHONE_ANDROID,
            'PayMaya': ft.Icons.PHONE_ANDROID,
        }
        
        payment_colors = {
            'Cash': 'primary',
            'Credit Card': 'secondary',
            'Debit Card': 'secondary',
            'Bank Transfer': 'tertiary',
            'GCash': 'primary',
            'PayMaya': 'primary',
        }
        
        icon = payment_icons.get(payment_method, ft.Icons.PAYMENT)
        color = payment_colors.get(payment_method, 'outline')
        
        # Format dates
        try:
            payment_dt = datetime.strptime(payment_date, "%Y-%m-%d %H:%M:%S")
            formatted_payment_date = payment_dt.strftime("%b %d, %Y at %I:%M %p")
        except:
            formatted_payment_date = payment_date or "N/A"
        
        return ft.Container(
            content=ft.Column([
                # Header row
                ft.Row([
                    ft.Icon(icon, color=color, size=32),
                    ft.Column([
                        ft.Row([
                            ft.Text(f"₱{amount:,.2f}", size=20, weight="bold", color="primary"),
                            ft.Container(
                                content=ft.Text(payment_method, size=11, weight="bold", color="white"),
                                bgcolor=color,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=10,
                            ),
                        ], spacing=10),
                        ft.Text(f"Invoice #{inv_number}", size=13, color="outline"),
                    ], spacing=2, expand=True),
                ], spacing=15),
                
                ft.Divider(height=10),
                
                # Payment details
                ft.Row([
                    ft.Column([
                        ft.Text("Patient", size=11, color="outline"),
                        ft.Text(patient_name, size=14, weight="bold"),
                    ], spacing=2),
                    ft.VerticalDivider(width=20),
                    ft.Column([
                        ft.Text("Processed By", size=11, color="outline"),
                        ft.Text(clerk_name or "System", size=14, weight="bold"),
                    ], spacing=2),
                    ft.VerticalDivider(width=20),
                    ft.Column([
                        ft.Text("Payment Date", size=11, color="outline"),
                        ft.Text(formatted_payment_date, size=14, weight="bold"),
                    ], spacing=2),
                ], spacing=10, wrap=True),
                
                # Actions
                ft.Row([
                    ft.TextButton(
                        "View Invoice",
                        icon=ft.Icons.RECEIPT,
                        on_click=lambda e, inv_id=inv_id: e.page.go(f"/billing/invoice/{inv_id}"),
                    ),
                    ft.TextButton(
                        "Print Receipt",
                        icon=ft.Icons.PRINT,
                        on_click=lambda e: print_receipt(e, inv_id),
                    ),
                ], spacing=5),
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    def print_receipt(e, inv_id):
        """Print receipt (placeholder)."""
        e.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Printing receipt for invoice #{inv_id}..."),
            bgcolor="primary",
        )
        e.page.snack_bar.open = True
        e.page.update()
        # TODO: Implement actual print functionality
    
    def load_payments(e=None):
        """Load and display payment history."""
        payments_container.controls.clear()
        
        payment_method = payment_method_filter.value
        date_start = date_from.value
        date_end = date_to.value
        search = search_field.value if search_field.value else ""
        
        payments = get_payments_from_db(payment_method, date_start, date_end, search)
        
        if payments:
            # Calculate totals
            total_revenue = sum(p[2] for p in payments)
            
            # Group by payment method
            payment_breakdown = {}
            for p in payments:
                method = p[3] or "Unknown"
                payment_breakdown[method] = payment_breakdown.get(method, 0) + p[2]
            
            # Summary header
            payments_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.PAYMENTS, color="primary", size=28),
                            ft.Column([
                                ft.Text(f"Total Revenue: ₱{total_revenue:,.2f}", size=20, weight="bold", color="primary"),
                                ft.Text(f"Showing {len(payments)} payment(s) from {date_start} to {date_end}", size=13, color="outline"),
                            ], spacing=2),
                        ], spacing=15),
                        
                        ft.Divider(height=15),
                        
                        # Payment method breakdown
                        ft.Text("Breakdown by Payment Method:", size=14, weight="bold"),
                        ft.Row([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(method, size=12, color="outline"),
                                    ft.Text(f"₱{amount:,.2f}", size=16, weight="bold", color="primary"),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                                padding=10,
                                border=ft.border.all(1, "outlineVariant"),
                                border_radius=8,
                            ) for method, amount in payment_breakdown.items()
                        ], spacing=10, wrap=True),
                    ], spacing=10),
                    padding=20,
                    bgcolor=ft.Colors.with_opacity(0.05, "primary"),
                    border_radius=10,
                    border=ft.border.all(1, "primary"),
                )
            )
            
            # Payment cards
            for payment in payments:
                payments_container.controls.append(create_payment_card(payment))
        else:
            payments_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF, size=80, color="outline"),
                        ft.Text("No payment history found", size=18, color="outline"),
                        ft.Text("Try adjusting your filters", size=14, color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                )
            )
        
        if e and hasattr(e, 'page'):
            e.page.update()
    
    # Initial load
    class FakePage:
        snack_bar = None
        def update(self): pass
        def go(self, route): pass
    
    load_payments(type('Event', (), {'page': FakePage()})())
    
    return ft.Column([
        NavigationHeader(
            "Payment History",
            "View all payment transactions and revenue",
            show_back=True,
            back_route="/billing/dashboard"
        ),
        
        ft.Container(
            content=ft.Column([
                # Info banner
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, color="primary"),
                        ft.Text(
                            "Track all payment transactions, view revenue by payment method, and manage receipts.",
                            size=13,
                            expand=True,
                        ),
                    ], spacing=10),
                    padding=15,
                    bgcolor=ft.Colors.with_opacity(0.1, "primary"),
                    border_radius=8,
                ),
                
                ft.Container(height=20),
                
                # Filters
                ft.Text("Filter Payments", size=20, weight="bold"),
                
                ft.Row([
                    payment_method_filter,
                    date_from,
                    date_to,
                ], spacing=10, wrap=True),
                
                ft.Row([
                    search_field,
                    ft.ElevatedButton(
                        "Apply Filters",
                        icon=ft.Icons.FILTER_ALT,
                        bgcolor="primary",
                        color="white",
                        on_click=load_payments,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        icon_color="primary",
                        tooltip="Refresh",
                        on_click=load_payments,
                    ),
                ], spacing=10),
                
                ft.Container(height=10),
                
                # Export options
                ft.Row([
                    ft.OutlinedButton(
                        "Export as CSV",
                        icon=ft.Icons.TABLE_CHART,
                        on_click=lambda e: export_payments(e, "csv"),
                    ),
                    ft.OutlinedButton(
                        "Export as PDF",
                        icon=ft.Icons.PICTURE_AS_PDF,
                        on_click=lambda e: export_payments(e, "pdf"),
                    ),
                ], spacing=10),
                
                ft.Divider(height=30),
                
                # Payments list
                payments_container,
            ], spacing=15),
            padding=20,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)

def export_payments(e, format):
    """Export payments (placeholder)."""
    e.page.snack_bar = ft.SnackBar(
        content=ft.Text(f"Exporting payments as {format.upper()}..."),
        bgcolor="primary",
    )
    e.page.snack_bar.open = True
    e.page.update()
    # TODO: Implement actual export functionality