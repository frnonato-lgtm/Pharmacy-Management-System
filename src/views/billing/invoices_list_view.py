"""View all invoices with comprehensive filtering and management."""

import flet as ft
from datetime import datetime
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader

def InvoicesListView():
    """Complete invoice management with filters and actions."""
    
    user = AppState.get_user()
    invoices_container = ft.Column(spacing=10)
    
    # --- FILTERS ---
    status_filter = ft.Dropdown(
        label="Status",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Unpaid"),
            ft.dropdown.Option("Paid"),
            ft.dropdown.Option("Partial"),
            ft.dropdown.Option("Cancelled"),
        ],
        value="All",
        width=150,
        border_color="primary",
    )
    
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
        border_color="primary",
    )
    
    date_from = ft.TextField(
        label="From Date",
        width=150,
        border_color="primary",
        hint_text="YYYY-MM-DD",
    )
    
    date_to = ft.TextField(
        label="To Date",
        width=150,
        border_color="primary",
        hint_text="YYYY-MM-DD",
    )
    
    search_field = ft.TextField(
        hint_text="Search by invoice #, patient name...",
        prefix_icon=ft.Icons.SEARCH,
        border_color="primary",
        expand=True,
    )
    
    # --- DB FUNCTION ---
    def get_invoices_from_db(status="All", payment_method="All", date_start="", date_end="", search=""):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT i.id, i.invoice_number, i.total_amount, i.status, i.created_at,
                   i.payment_method, i.payment_date, i.subtotal, i.tax, i.discount,
                   u.full_name as patient_name, u.id as patient_id
            FROM invoices i
            LEFT JOIN users u ON i.patient_id = u.id
            WHERE 1=1
        """
        
        params = []
        
        if status != "All":
            query += " AND i.status = ?"
            params.append(status)
        
        if payment_method != "All":
            query += " AND i.payment_method = ?"
            params.append(payment_method)
        
        if date_start:
            query += " AND DATE(i.created_at) >= ?"
            params.append(date_start)
        
        if date_end:
            query += " AND DATE(i.created_at) <= ?"
            params.append(date_end)
        
        if search:
            query += " AND (i.invoice_number LIKE ? OR u.full_name LIKE ?)"
            params.append(f"%{search}%")
            params.append(f"%{search}%")
        
        query += " ORDER BY i.created_at DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    # --- CARD CREATOR ---
    def create_invoice_card(inv):
        inv_id, inv_number, total, status, created_at, payment_method, payment_date, subtotal, tax, discount, patient_name, patient_id = inv
        
        status_colors = {
            "Paid": "primary",
            "Unpaid": "error",
            "Partial": "tertiary",
            "Cancelled": "outline",
        }
        status_color = status_colors.get(status, "outline")
        
        formatted_date = created_at
        
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Row([
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.RECEIPT, color="primary", size=20),
                            ft.Text(f"Invoice #{inv_number}", size=16, weight="bold"),
                        ], spacing=5),
                        ft.Text(f"Patient: {patient_name} (ID: {patient_id})", size=13, color="outline"),
                    ], spacing=2, expand=True),
                    ft.Container(
                        content=ft.Text(status, size=12, weight="bold", color="white"),
                        bgcolor=status_color,
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=15,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(height=10),
                
                # Totals
                ft.Row([
                    ft.Column([
                        ft.Text("Subtotal", size=11, color="outline"),
                        ft.Text(f"₱{subtotal:,.2f}", size=14, weight="bold"),
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Tax (12%)", size=11, color="outline"),
                        ft.Text(f"₱{tax:,.2f}", size=14, weight="bold"),
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Total", size=11, color="outline"),
                        ft.Text(f"₱{total:,.2f}", size=16, weight="bold", color="primary"),
                    ], spacing=2),
                ], spacing=20, wrap=True),
                
                ft.Container(height=5),
                
                # Payment Date info
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=14, color="primary"),
                        ft.Text(f"Paid on: {payment_date}", size=12, italic=True),
                    ], spacing=5),
                    visible=status == "Paid",
                    bgcolor=ft.Colors.with_opacity(0.1, "primary"),
                    padding=8,
                    border_radius=5,
                ),
                
                # Buttons
                ft.Row([
                    ft.ElevatedButton(
                        "View Details",
                        icon=ft.Icons.VISIBILITY,
                        bgcolor="primary",
                        color="white",
                        on_click=lambda e, inv_id=inv_id: view_invoice_detail(e, inv_id),
                    ),
                    
                    # Mark as Paid
                    ft.OutlinedButton(
                        "Mark as Paid",
                        icon=ft.Icons.PAYMENT,
                        disabled=(status == "Paid" or status == "Cancelled"),
                        on_click=lambda e, inv_id=inv_id: mark_as_paid(e, inv_id),
                    ),
                    
                    # Cancel Button
                    ft.TextButton(
                        "Cancel Invoice",
                        icon=ft.Icons.DELETE,
                        icon_color="error",
                        style=ft.ButtonStyle(color="error"),
                        disabled=(status == "Paid" or status == "Cancelled"),
                        on_click=lambda e, inv_id=inv_id: cancel_invoice(e, inv_id),
                    ),
                ], spacing=10, wrap=True),
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    # --- HELPERS ---
    def view_invoice_detail(e, inv_id):
        e.page.go(f"/billing/invoice/{inv_id}")
    
    def mark_as_paid(e, inv_id):
        conn = get_db_connection()
        conn.execute("""
            UPDATE invoices 
            SET status = 'Paid',
                payment_date = ?
            WHERE id = ?
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inv_id))
        
        conn.commit()
        conn.close()
        
        e.page.snack_bar = ft.SnackBar(content=ft.Text("Marked as Paid!"), bgcolor="primary")
        e.page.snack_bar.open = True
        e.page.update()
        
        load_invoices(e)
    
    def cancel_invoice(e, inv_id):
        conn = get_db_connection()
        conn.execute("UPDATE invoices SET status = 'Cancelled' WHERE id = ?", (inv_id,))
        conn.commit()
        conn.close()
        
        e.page.snack_bar = ft.SnackBar(content=ft.Text("Invoice Cancelled!"), bgcolor="error")
        e.page.snack_bar.open = True
        e.page.update()
        
        load_invoices(e)
    
    # --- LOAD INVOICES ---
    def load_invoices(e=None):
        invoices_container.controls.clear()
        
        invoices = get_invoices_from_db(
            status_filter.value,
            payment_method_filter.value,
            date_from.value,
            date_to.value,
            search_field.value
        )
        
        if invoices:
            total_amount = sum(inv[2] for inv in invoices)
            
            invoices_container.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, color="primary"),
                        ft.Text(f"Showing {len(invoices)} invoice(s) | Total: ₱{total_amount:,.2f}", weight="bold"),
                    ]),
                    padding=15,
                    bgcolor=ft.Colors.with_opacity(0.05, "primary"),
                    border_radius=8,
                )
            )
            
            for inv in invoices:
                invoices_container.controls.append(create_invoice_card(inv))
        else:
            # Centered empty state
            invoices_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF, size=80, color="outline"),
                        ft.Text("No invoices found", size=18, color="outline"),
                        ft.Text("Try adjusting your filters or create a new invoice", size=14, color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.alignment.center, 
                )
            )
        
        # Only update the page if an event 'e' exists
        if e: 
            e.page.update()
    
    # FIX: Pass 'None' for initial load instead of a Fake class
    load_invoices(None)
    
    # --- PAGE LAYOUT ---
    return ft.Column([
        NavigationHeader(
            "All Invoices",
            "View and manage all billing invoices",
            show_back=False,
        ),
        
        ft.Container(
            content=ft.Column([
                # Create Button
                ft.Row([
                    ft.ElevatedButton(
                        "Create New Invoice",
                        icon=ft.Icons.ADD,
                        bgcolor="primary",
                        color="white",
                        on_click=lambda e: e.page.go("/billing/create-invoice"),
                    )
                ]),
                
                ft.Container(height=20),
                
                # Filters
                ft.Text("Filter Invoices", size=20, weight="bold"),
                
                ft.Row([
                    status_filter,
                    payment_method_filter,
                    date_from,
                    date_to,
                ], spacing=10, wrap=True),
                
                # Search Bar
                ft.Row([
                    search_field,
                    ft.ElevatedButton(
                        "Apply Filters",
                        icon=ft.Icons.FILTER_ALT,
                        bgcolor="primary",
                        color="white",
                        on_click=load_invoices,
                    ),
                ], spacing=10),
                
                ft.Divider(height=30),
                
                # The List
                invoices_container,
            ], spacing=15),
            padding=20,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)