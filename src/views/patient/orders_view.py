"""Orders history view with real database integration."""

import flet as ft
from state import AppState
from services.database import get_db_connection
from datetime import datetime

def OrdersView():
    """Orders history and tracking view with live data."""
    
    # Get current logged-in user
    user = AppState.get_user()
    if not user:
        return ft.Text("Please log in first", color="error")
    
    user_id = user['id']
    
    # State for filter
    current_filter = {"value": "All"}
    orders_container = ft.Column(spacing=15)
    
    def load_orders(filter_status="All"):
        """Load orders from database based on filter."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query based on filter
        if filter_status == "All":
            cursor.execute("""
                SELECT 
                    o.id,
                    o.order_date,
                    o.status,
                    o.total_amount,
                    o.payment_method,
                    GROUP_CONCAT(m.name || ' x' || oi.quantity, ', ') as items
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                LEFT JOIN medicines m ON oi.medicine_id = m.id
                WHERE o.patient_id = ?
                GROUP BY o.id
                ORDER BY o.order_date DESC
            """, (user_id,))
        elif filter_status == "Pending":
            cursor.execute("""
                SELECT 
                    o.id,
                    o.order_date,
                    o.status,
                    o.total_amount,
                    o.payment_method,
                    GROUP_CONCAT(m.name || ' x' || oi.quantity, ', ') as items
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                LEFT JOIN medicines m ON oi.medicine_id = m.id
                WHERE o.patient_id = ? AND o.status IN ('Pending', 'Processing')
                GROUP BY o.id
                ORDER BY o.order_date DESC
            """, (user_id,))
        else:  # Completed
            cursor.execute("""
                SELECT 
                    o.id,
                    o.order_date,
                    o.status,
                    o.total_amount,
                    o.payment_method,
                    GROUP_CONCAT(m.name || ' x' || oi.quantity, ', ') as items
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                LEFT JOIN medicines m ON oi.medicine_id = m.id
                WHERE o.patient_id = ? AND o.status = 'Completed'
                GROUP BY o.id
                ORDER BY o.order_date DESC
            """, (user_id,))
        
        orders = cursor.fetchall()
        conn.close()
        
        return orders
    
    def format_date(date_str):
        """Format date string nicely."""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%b %d, %Y")
        except:
            return date_str
    
    def get_status_color(status):
        """Get color for order status."""
        colors = {
            'Pending': 'tertiary',
            'Processing': 'secondary',
            'Ready': 'primary',
            'Completed': 'outline',
            'Cancelled': 'error'
        }
        return colors.get(status, 'outline')
    
    def create_order_card(order):
        """Create order card from database row."""
        order_id = order[0]
        order_date = format_date(order[1])
        status = order[2]
        total = order[3]
        items = order[5] if order[5] else "No items"
        
        status_color = get_status_color(status)
        
        # Parse items into list
        items_list = items.split(', ') if items != "No items" else []
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text(f"Order #{order_id}", size=18, weight="bold"),
                        ft.Text(order_date, size=12, color="outline"),
                    ], spacing=2),
                    ft.Container(
                        content=ft.Text(
                            status,
                            size=12,
                            weight="bold",
                            color="onPrimaryContainer",
                        ),
                        bgcolor=ft.Colors.with_opacity(0.2, status_color),
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=15,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(),
                
                ft.Column([
                    ft.Text("Items:", size=13, weight="bold", color="outline"),
                    *([ft.Text(f"• {item}", size=13) for item in items_list] if items_list else [ft.Text("No items", size=13, color="outline")]),
                ], spacing=5),
                
                ft.Divider(),
                
                ft.Row([
                    ft.Text("Total:", size=14, weight="bold"),
                    ft.Text(f"₱ {total:.2f}", size=16, weight="bold", color="primary"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    def view_order_details(e, order_id):
        """Show order details dialog."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get order details
        cursor.execute("""
            SELECT 
                o.id,
                o.order_date,
                o.status,
                o.total_amount,
                o.payment_method,
                o.payment_status,
                o.notes
            FROM orders o
            WHERE o.id = ?
        """, (order_id,))
        order = cursor.fetchone()
        
        # Get order items
        cursor.execute("""
            SELECT 
                m.name,
                oi.quantity,
                oi.unit_price,
                oi.subtotal
            FROM order_items oi
            JOIN medicines m ON oi.medicine_id = m.id
            WHERE oi.order_id = ?
        """, (order_id,))
        items = cursor.fetchall()
        conn.close()
        
        if not order:
            return
        
        # Build items list
        items_widgets = []
        for item in items:
            items_widgets.append(
                ft.Row([
                    ft.Text(f"{item[0]} x{item[1]}", expand=True),
                    ft.Text(f"₱{item[3]:.2f}", weight="bold"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        
        # Show dialog
        dialog = ft.AlertDialog(
            title=ft.Text(f"Order #{order_id} Details"),
            content=ft.Column([
                ft.Text(f"Date: {format_date(order[1])}", size=13),
                ft.Text(f"Status: {order[2]}", size=13),
                ft.Text(f"Payment: {order[4] or 'Not specified'}", size=13),
                ft.Divider(),
                ft.Text("Items:", weight="bold"),
                *items_widgets,
                ft.Divider(),
                ft.Row([
                    ft.Text("Total:", weight="bold"),
                    ft.Text(f"₱{order[3]:.2f}", weight="bold", color="primary"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=10, tight=True),
            actions=[
                ft.TextButton("Close", on_click=lambda e: close_dialog(e)),
            ],
        )
        
        e.page.dialog = dialog
        dialog.open = True
        e.page.update()
    
    def close_dialog(e):
        e.page.dialog.open = False
        e.page.update()
    
    def update_orders_list(e=None):
        """Refresh orders list based on current filter."""
        orders = load_orders(current_filter["value"])
        orders_container.controls.clear()
        
        if orders:
            for order in orders:
                orders_container.controls.append(create_order_card(order))
        else:
            orders_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=80, color="outline"),
                        ft.Text("No orders found", size=18, color="outline"),
                        ft.Text(f"You don't have any {current_filter['value'].lower()} orders yet", 
                               size=14, color="outline"),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "Start Shopping",
                            icon=ft.Icons.SHOPPING_BAG,
                            on_click=lambda e: e.page.go("/patient/search"),
                            bgcolor="primary",
                            color="onPrimary",
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.alignment.center,
                )
            )
        
        if e:
            e.page.update()
    
    def filter_button_click(e, status):
        """Handle filter button click."""
        current_filter["value"] = status
        update_orders_list(e)
    
    # Initial load
    update_orders_list()
    
    return ft.Column([
        ft.Text("My Orders", size=28, weight="bold"),
        ft.Text("View and track your medicine orders", size=14, color="outline"),
        
        ft.Container(height=20),
        
        # Filter tabs
        ft.Row([
            ft.ElevatedButton(
                "All Orders", 
                bgcolor="primary" if current_filter["value"] == "All" else None,
                color="onPrimary" if current_filter["value"] == "All" else None,
                on_click=lambda e: filter_button_click(e, "All")
            ),
            ft.OutlinedButton(
                "Pending",
                on_click=lambda e: filter_button_click(e, "Pending")
            ),
            ft.OutlinedButton(
                "Completed",
                on_click=lambda e: filter_button_click(e, "Completed")
            ),
        ], spacing=10),
        
        ft.Container(height=20),
        
        # Orders list (dynamic)
        orders_container,
    ], scroll=ft.ScrollMode.AUTO, spacing=0)