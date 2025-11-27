"""Orders history view."""

import flet as ft

def OrdersView():
    """Orders history and tracking view."""
    
    # Sample orders
    orders = [
        {
            "id": "ORD-1234",
            "date": "Nov 20, 2025",
            "items": ["Paracetamol 500mg x2", "Vitamin C"],
            "total": 18.00,
            "status": "Ready for Pickup",
            "status_color": "primary",
        },
        {
            "id": "ORD-1233",
            "date": "Nov 18, 2025",
            "items": ["Amoxicillin 250mg"],
            "total": 15.00,
            "status": "Processing",
            "status_color": "tertiary",
        },
        {
            "id": "ORD-1232",
            "date": "Nov 15, 2025",
            "items": ["Ibuprofen 400mg x3"],
            "total": 22.50,
            "status": "Completed",
            "status_color": "outline",
        },
    ]
    
    def create_order_card(order):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text(order['id'], size=18, weight="bold"),
                        ft.Text(order['date'], size=12, color="outline"),
                    ], spacing=2),
                    ft.Container(
                        content=ft.Text(
                            order['status'],
                            size=12,
                            weight="bold",
                            color="onPrimaryContainer" if order['status_color'] == "primary" else "onSurfaceVariant",
                        ),
                        bgcolor=ft.Colors.with_opacity(0.2, order['status_color']),
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=15,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(),
                
                ft.Column([
                    ft.Text("Items:", size=13, weight="bold", color="outline"),
                    *[ft.Text(f"• {item}", size=13) for item in order['items']],
                ], spacing=5),
                
                ft.Divider(),
                
                ft.Row([
                    ft.Text("Total:", size=14, weight="bold"),
                    ft.Text(f"₱ {order['total']:.2f}", size=16, weight="bold", color="primary"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Row([
                    ft.TextButton("View Details", icon=ft.Icons.VISIBILITY),
                    ft.OutlinedButton("Track Order", icon=ft.Icons.LOCAL_SHIPPING),
                ], alignment=ft.MainAxisAlignment.END, spacing=5),
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    return ft.Column([
        ft.Text("My Orders", size=28, weight="bold"),
        ft.Text("View and track your medicine orders", size=14, color="outline"),
        
        ft.Container(height=20),
        
        # Filter tabs
        ft.Row([
            ft.ElevatedButton("All Orders", bgcolor="primary", color="onPrimary"),
            ft.OutlinedButton("Pending"),
            ft.OutlinedButton("Completed"),
        ], spacing=10),
        
        ft.Container(height=20),
        
        # Orders list
        ft.Column([create_order_card(order) for order in orders], spacing=15),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)