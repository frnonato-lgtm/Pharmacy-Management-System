"""Shopping cart view."""

import flet as ft

def CartView():
    """Shopping cart view."""
    
    # Sample cart items (in real app, this would come from database/state)
    cart_items = [
        {"id": 1, "name": "Paracetamol 500mg", "price": 5.00, "quantity": 2},
        {"id": 2, "name": "Vitamin C 500mg", "price": 8.00, "quantity": 1},
    ]
    
    def create_cart_item(item):
        quantity_field = ft.TextField(
            value=str(item['quantity']),
            width=60,
            text_align=ft.TextAlign.CENTER,
            border_color="outline",
        )
        
        return ft.Container(
            content=ft.Row([
                # Item image
                ft.Container(
                    width=60,
                    height=60,
                    bgcolor="surfaceVariant",
                    border_radius=8,
                    content=ft.Icon(ft.Icons.MEDICATION, size=30, color="outline"),
                    alignment=ft.alignment.center,
                ),
                # Item details
                ft.Column([
                    ft.Text(item['name'], size=16, weight="bold"),
                    ft.Text(f"₱ {item['price']:.2f}", size=14, color="primary"),
                ], spacing=5, expand=True),
                # Quantity controls
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.REMOVE,
                        icon_size=16,
                        icon_color="primary",
                    ),
                    quantity_field,
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_size=16,
                        icon_color="primary",
                    ),
                ], spacing=5),
                # Subtotal
                ft.Text(
                    f"₱ {item['price'] * item['quantity']:.2f}",
                    size=16,
                    weight="bold",
                    color="primary",
                ),
                # Remove button
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color="error",
                    tooltip="Remove from cart",
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=15),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    # Calculate totals
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    tax = subtotal * 0.12  # 12% tax
    total = subtotal + tax
    
    if not cart_items:
        return ft.Column([
            ft.Text("Shopping Cart", size=28, weight="bold"),
            ft.Container(height=20),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, size=100, color="outline"),
                    ft.Text("Your cart is empty", size=20, color="outline"),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Browse Medicines",
                        icon=ft.Icons.SEARCH,
                        on_click=lambda e: e.page.go("/patient/search"),
                        bgcolor="primary",
                        color="onPrimary",
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=80,
                alignment=ft.alignment.center,
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)
    
    return ft.Column([
        ft.Row([
            ft.Text("Shopping Cart", size=28, weight="bold"),
            ft.Text(f"({len(cart_items)} items)", size=18, color="outline"),
        ], spacing=10),
        
        ft.Container(height=20),
        
        # Cart items
        ft.Column([create_cart_item(item) for item in cart_items], spacing=10),
        
        ft.Container(height=20),
        ft.Divider(),
        
        # Order summary
        ft.Container(
            content=ft.Column([
                ft.Text("Order Summary", size=20, weight="bold"),
                ft.Divider(),
                ft.Row([
                    ft.Text("Subtotal:", size=14),
                    ft.Text(f"₱ {subtotal:.2f}", size=14, weight="bold"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text("Tax (12%):", size=14),
                    ft.Text(f"₱ {tax:.2f}", size=14, weight="bold"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Row([
                    ft.Text("Total:", size=18, weight="bold"),
                    ft.Text(f"₱ {total:.2f}", size=20, weight="bold", color="primary"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Proceed to Checkout",
                    width=300,
                    height=50,
                    icon=ft.Icons.PAYMENT,
                    bgcolor="primary",
                    color="onPrimary",
                    on_click=lambda e: e.page.go("/patient/checkout"),
                ),
                ft.OutlinedButton(
                    "Continue Shopping",
                    width=300,
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: e.page.go("/patient/search"),
                ),
            ], spacing=10),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
            width=400,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)