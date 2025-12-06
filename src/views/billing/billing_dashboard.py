"""Billing dashboard with comprehensive billing features."""

import flet as ft
from datetime import datetime, timedelta
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader

def BillingDashboard():
    """Main billing dashboard with statistics and quick actions."""
    
    user = AppState.get_user()
    user_name = user['full_name'] if user else "Billing Clerk"
    
    # Get statistics from database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count pending invoices
    cursor.execute("SELECT COUNT(*) FROM invoices WHERE status = 'Unpaid'")
    result = cursor.fetchone()
    pending_invoices = result[0] if result else 0
    
    # Count paid invoices today
    cursor.execute("""
        SELECT COUNT(*) FROM invoices 
        WHERE status = 'Paid' 
        AND DATE(payment_date) = DATE('now')
    """)
    result = cursor.fetchone()
    paid_today = result[0] if result else 0
    
    # Calculate today's revenue
    cursor.execute("""
        SELECT COALESCE(SUM(total_amount), 0) FROM invoices 
        WHERE status = 'Paid' 
        AND DATE(payment_date) = DATE('now')
    """)
    result = cursor.fetchone()
    revenue_today = result[0] if result else 0.0
    
    # Calculate pending amount
    cursor.execute("""
        SELECT COALESCE(SUM(total_amount), 0) FROM invoices 
        WHERE status = 'Unpaid'
    """)
    result = cursor.fetchone()
    pending_amount = result[0] if result else 0.0
    
    # Get recent invoices
    cursor.execute("""
        SELECT i.id, i.invoice_number, i.total_amount, i.status, i.created_at,
               u.full_name as patient_name
        FROM invoices i
        LEFT JOIN users u ON i.patient_id = u.id
        ORDER BY i.created_at DESC
        LIMIT 5
    """)
    recent_invoices = cursor.fetchall()
    
    # Get recent activity
    cursor.execute("""
        SELECT action, details, timestamp
        FROM activity_log
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 5
    """, (user['id'],))
    recent_activities = cursor.fetchall()
    
    conn.close()
    
    # Helper: Create stat card
    def create_stat_card(title, value, icon, color, subtitle="", is_currency=False):
        display_value = f"₱{value:,.2f}" if is_currency else str(value)
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=40),
                    ft.Column([
                        ft.Text(title, size=14, color="outline"),
                        ft.Text(
                            display_value,
                            size=28 if is_currency else 32,
                            weight="bold",
                            color=color,
                        ),
                        ft.Text(subtitle, size=11, color="outline") if subtitle else ft.Container(),
                    ], spacing=2, expand=True),
                ], spacing=15),
            ]),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
            expand=True,
        )
    
    # Helper: Create quick action button
    def create_action_button(text, icon, route, color):
        return ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(icon, color="onPrimary"),
                ft.Text(text, color="onPrimary"),
            ], spacing=10),
            bgcolor=color,
            on_click=lambda e: e.page.go(route),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=15,
            ),
        )
    
    # Helper: Create invoice item
    def create_invoice_item(inv):
        status_colors = {
            "Paid": "primary",
            "Unpaid": "error",
            "Partial": "tertiary",
            "Cancelled": "outline",
        }
        status_color = status_colors.get(inv[3], "outline")
        
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(f"Invoice #{inv[1]}", weight="bold", size=14),
                    ft.Text(f"Patient: {inv[5]}", size=12, color="outline"),
                    ft.Text(f"Amount: ₱{inv[2]:,.2f}", size=13, weight="bold", color="primary"),
                    ft.Text(f"Date: {inv[4]}", size=11, color="outline", italic=True),
                ], spacing=3, expand=True),
                ft.Container(
                    content=ft.Text(inv[3], size=12, weight="bold", color="white"),
                    bgcolor=status_color,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border_radius=15,
                ),
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD,
                    icon_color="primary",
                    tooltip="View Invoice",
                    on_click=lambda e, inv_id=inv[0]: e.page.go(f"/billing/invoice/{inv_id}"),
                ),
            ], spacing=10),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
            bgcolor="surface",
        )
    
    # Helper: Create activity item
    def create_activity_item(action, details, timestamp):
        action_icons = {
            'invoice_created': '📄',
            'payment_received': '💰',
            'invoice_cancelled': '❌',
            'payment_processed': '✓',
        }
        icon = action_icons.get(action, '•')
        
        return ft.Text(
            f"{icon} {details}",
            size=12,
            color="outline",
        )
    
    # Build recent invoices list
    invoice_widgets = []
    if recent_invoices:
        for inv in recent_invoices:
            invoice_widgets.append(create_invoice_item(inv))
    else:
        invoice_widgets.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.RECEIPT_LONG, size=60, color="outline"),
                    ft.Text("No recent invoices", size=16, color="outline"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=30,
            )
        )
    
    # Build activity list
    activity_widgets = []
    if recent_activities:
        for activity in recent_activities:
            activity_widgets.append(create_activity_item(activity[0], activity[1], activity[2]))
    else:
        activity_widgets.append(
            ft.Text("No recent activity", size=12, color="outline", italic=True)
        )
    
    return ft.Column([
        # Navigation header (no back button on dashboard)
        NavigationHeader(
            f"Welcome, {user_name}",
            "Billing Dashboard - Manage invoices and payments",
            show_back=False,
        ),
        
        ft.Container(
            content=ft.Column([
                # Statistics cards
                ft.Row([
                    create_stat_card(
                        "Pending Invoices",
                        pending_invoices,
                        ft.Icons.PENDING_ACTIONS,
                        "error",
                        "Awaiting payment"
                    ),
                    create_stat_card(
                        "Paid Today",
                        paid_today,
                        ft.Icons.CHECK_CIRCLE,
                        "primary",
                        "Completed transactions"
                    ),
                    create_stat_card(
                        "Today's Revenue",
                        revenue_today,
                        ft.Icons.ATTACH_MONEY,
                        "primary",
                        is_currency=True
                    ),
                    create_stat_card(
                        "Pending Amount",
                        pending_amount,
                        ft.Icons.MONEY_OFF,
                        "error",
                        is_currency=True
                    ),
                ], spacing=15),
                
                ft.Container(height=20),
                
                # Quick actions
                ft.Container(
                    content=ft.Column([
                        ft.Text("Quick Actions", size=20, weight="bold"),
                        ft.Row([
                            create_action_button(
                                "View All Invoices"
                                ,
                                ft.Icons.ADD_CARD,
                                "/billing/create-invoice",
                                "primary",
                            ),
                            create_action_button(
                                "Create Invoice",
                                ft.Icons.RECEIPT_LONG,
                                "/billing/invoices",
                                "secondary",
                            ),
                            create_action_button(
                                "Payment History",
                                ft.Icons.HISTORY,
                                "/billing/payments",
                                "tertiary",
                            ),
                            create_action_button(
                                "Generate Report",
                                ft.Icons.ANALYTICS,
                                "/billing/reports",
                                "primary",
                            ),
                        ], spacing=15, wrap=True),
                    ], spacing=15),
                    padding=20,
                    bgcolor="surface",
                    border_radius=10,
                    border=ft.border.all(1, "outlineVariant"),
                ),
                
                ft.Container(height=20),
                
                # Main content area
                ft.Row([
                    # Recent invoices
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.RECEIPT, color="primary", size=24),
                                ft.Text("Recent Invoices", size=20, weight="bold"),
                            ], spacing=10),
                            ft.Divider(),
                            
                            *invoice_widgets,
                            
                            ft.Container(height=10),
                            ft.TextButton(
                                "View All Invoices →",
                                on_click=lambda e: e.page.go("/billing/invoices"),
                            ),
                        ], spacing=10),
                        padding=20,
                        bgcolor="surface",
                        border_radius=10,
                        border=ft.border.all(1, "outlineVariant"),
                        expand=2,
                    ),
                    
                    # Activity and quick stats
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.HISTORY, color="primary", size=24),
                                ft.Text("Recent Activity", size=20, weight="bold"),
                            ], spacing=10),
                            ft.Divider(),
                            
                            ft.Container(
                                content=ft.Column(
                                    activity_widgets,
                                    spacing=8,
                                ),
                                padding=10,
                                border=ft.border.all(1, "outlineVariant"),
                                border_radius=8,
                            ),
                            
                            ft.Container(height=15),
                            
                            # Payment methods breakdown
                            ft.Text("Payment Methods Today", size=16, weight="bold"),
                            ft.Divider(height=10),
                            
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Icon(ft.Icons.MONEY, color="primary", size=20),
                                        ft.Text("Cash", size=13),
                                        ft.Text("₱0.00", size=13, weight="bold", color="primary"),
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    ft.Row([
                                        ft.Icon(ft.Icons.CREDIT_CARD, color="secondary", size=20),
                                        ft.Text("Card", size=13),
                                        ft.Text("₱0.00", size=13, weight="bold", color="secondary"),
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    ft.Row([
                                        ft.Icon(ft.Icons.ACCOUNT_BALANCE, color="tertiary", size=20),
                                        ft.Text("Bank Transfer", size=13),
                                        ft.Text("₱0.00", size=13, weight="bold", color="tertiary"),
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ], spacing=10),
                                padding=10,
                                border=ft.border.all(1, "outlineVariant"),
                                border_radius=8,
                            ),
                        ], spacing=10),
                        padding=20,
                        bgcolor="surface",
                        border_radius=10,
                        border=ft.border.all(1, "outlineVariant"),
                        expand=1,
                    ),
                ], spacing=15, vertical_alignment=ft.CrossAxisAlignment.START),
            ], spacing=0),
            padding=20,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)