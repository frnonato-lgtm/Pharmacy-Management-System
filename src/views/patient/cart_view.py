"""Shopping cart view with real database integration."""

import flet as ft
from state import AppState
from services.database import get_db_connection

def CartView():
    """Shopping cart view with persistent cart data."""
    
    # Get current logged-in user
    user = AppState.get_user()
    if not user:
        return ft.Text("Please log in first", color="error")
    
    user_id = user['id']
    
    # Cart state
    cart_container = ft.Column(spacing=10)
    summary_container = ft.Container()
    
    def load_cart():
        """Load cart items from database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if cart table exists, if not create it
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                medicine_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users(id),
                FOREIGN KEY (medicine_id) REFERENCES medicines(id)
            )
        """)
        
        # Get cart items with medicine details
        cursor.execute("""
            SELECT 
                c.id,
                c.medicine_id,
                m.name,
                m.price,
                c.quantity,
                m.stock
            FROM cart c
            JOIN medicines m ON c.medicine_id = m.id
            WHERE c.patient_id = ?
        """, (user_id,))
        
        items = cursor.fetchall()
        conn.close()
        
        return items
    
    def update_quantity(cart_id, medicine_id, new_quantity, stock, e):
        """Update item quantity in cart."""
        if new_quantity <= 0:
            remove_from_cart(cart_id, e)
            return
        
        if new_quantity > stock:
            show_snackbar(e, f"Only {stock} items available in stock", error=True)
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE cart SET quantity = ? WHERE id = ?", (new_quantity, cart_id))
        conn.commit()
        conn.close()
        
        refresh_cart(e)
    
    def remove_from_cart(cart_id, e):
        """Remove item from cart."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart WHERE id = ?", (cart_id,))
        conn.commit()
        conn.close()
        
        show_snackbar(e, "Item removed from cart")
        refresh_cart(e)
    
    def show_snackbar(e, message, error=False):
        """Show snackbar notification."""
        e.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor="error" if error else "primary",
        )
        e.page.snack_bar.open = True
        e.page.update()
    
    def create_cart_item(item):
        """Create cart item widget."""
        cart_id = item[0]
        medicine_id = item[1]
        name = item[2]
        price = item[3]
        quantity = item[4]
        stock = item[5]
        
        quantity_field = ft.TextField(
            value=str(quantity),
            width=60,
            text_align=ft.TextAlign.CENTER,
            border_color="outline",
            on_submit=lambda e: update_quantity(cart_id, medicine_id, int(e.control.value), stock, e)
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
                    ft.Text(name, size=16, weight="bold"),
                    ft.Text(f"₱ {price:.2f}", size=14, color="primary"),
                    ft.Text(f"Available: {stock}", size=11, color="outline"),
                ], spacing=5, expand=True),
                # Quantity controls
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.REMOVE,
                        icon_size=16,
                        icon_color="primary",
                        on_click=lambda e: update_quantity(cart_id, medicine_id, quantity - 1, stock, e)
                    ),
                    quantity_field,
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_size=16,
                        icon_color="primary",
                        on_click=lambda e: update_quantity(cart_id, medicine_id, quantity + 1, stock, e)
                    ),
                ], spacing=5),
                # Subtotal
                ft.Text(
                    f"₱ {price * quantity:.2f}",
                    size=16,
                    weight="bold",
                    color="primary",
                ),
                # Remove button
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color="error",
                    tooltip="Remove from cart",
                    on_click=lambda e: remove_from_cart(cart_id, e)
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=15),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    def proceed_to_checkout(e):
        """Handle checkout process."""
        items = load_cart()
        if not items:
            show_snackbar(e, "Cart is empty", error=True)
            return
        
        # Create order from cart
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Calculate total
            subtotal = sum(item[3] * item[4] for item in items)
            tax = subtotal * 0.12
            total = subtotal + tax
            
            # Create order
            cursor.execute("""
                INSERT INTO orders (patient_id, total_amount, status, payment_status)
                VALUES (?, ?, 'Pending', 'Unpaid')
            """, (user_id, total))
            
            order_id = cursor.lastrowid
            
            # Add order items and update stock
            for item in items:
                medicine_id = item[1]
                quantity = item[4]
                unit_price = item[3]
                subtotal_item = unit_price * quantity
                
                # Check stock
                cursor.execute("SELECT stock FROM medicines WHERE id = ?", (medicine_id,))
                current_stock = cursor.fetchone()[0]
                
                if current_stock < quantity:
                    raise Exception(f"Insufficient stock for {item[2]}")
                
                # Add order item
                cursor.execute("""
                    INSERT INTO order_items (order_id, medicine_id, quantity, unit_price, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """, (order_id, medicine_id, quantity, unit_price, subtotal_item))
                
                # Update stock
                cursor.execute("""
                    UPDATE medicines 
                    SET stock = stock - ? 
                    WHERE id = ?
                """, (quantity, medicine_id))
            
            # Clear cart
            cursor.execute("DELETE FROM cart WHERE patient_id = ?", (user_id,))
            
            conn.commit()
            
            show_snackbar(e, f"Order #{order_id} created successfully!")
            refresh_cart(e)
            
            # Navigate to orders page
            e.page.go("/patient/orders")
            
        except Exception as ex:
            conn.rollback()
            show_snackbar(e, f"Checkout failed: {str(ex)}", error=True)
        finally:
            conn.close()
    
    def refresh_cart(e):
        """Refresh cart display."""
        items = load_cart()
        
        cart_container.controls.clear()
        
        if items:
            for item in items:
                cart_container.controls.append(create_cart_item(item))
            
            # Calculate totals
            subtotal = sum(item[3] * item[4] for item in items)
            tax = subtotal * 0.12
            total = subtotal + tax
            
            # Update summary
            summary_container.content = ft.Column([
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
                    on_click=proceed_to_checkout,
                ),
                ft.OutlinedButton(
                    "Continue Shopping",
                    width=300,
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: e.page.go("/patient/search"),
                ),
            ], spacing=10)
        else:
            summary_container.content = ft.Column([
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
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
        
        e.page.update()
    
    # Initial load
    items = load_cart()
    
    if not items:
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
    
    # Build initial cart display
    for item in items:
        cart_container.controls.append(create_cart_item(item))
    
    # Calculate initial totals
    subtotal = sum(item[3] * item[4] for item in items)
    tax = subtotal * 0.12
    total = subtotal + tax
    
    summary_container.content = ft.Column([
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
            on_click=proceed_to_checkout,
        ),
        ft.OutlinedButton(
            "Continue Shopping",
            width=300,
            icon=ft.Icons.ARROW_BACK,
            on_click=lambda e: e.page.go("/patient/search"),
        ),
    ], spacing=10)
    
    return ft.Column([
        ft.Row([
            ft.Text("Shopping Cart", size=28, weight="bold"),
            ft.Text(f"({len(items)} items)", size=18, color="outline"),
        ], spacing=10),
        
        ft.Container(height=20),
        
        # Cart items
        cart_container,
        
        ft.Container(height=20),
        ft.Divider(),
        
        # Order summary
        ft.Container(
            content=summary_container,
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
            width=400,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)