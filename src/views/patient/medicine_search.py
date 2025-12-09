"""Medicine search and browse view with add to cart functionality."""

import flet as ft
from state import AppState
from services.database import get_db_connection

def MedicineSearch():
    """Medicine search and browse view with cart integration."""
    
    # checking if the user is actually logged in
    user = AppState.get_user()
    if not user:
        return ft.Text("Please log in first", color="error")
    
    user_id = user['id']
    
    # search bar for finding meds
    search_field = ft.TextField(
        hint_text="Search medicines by name...",
        prefix_icon=ft.Icons.SEARCH,
        border_color="primary", # need this so it shows up in dark mode
        expand=True,
    )
    
    # dropdown to filter by category
    category_dropdown = ft.Dropdown(
        label="Category",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Pain Relief"),
            ft.dropdown.Option("Cough & Cold"),
            ft.dropdown.Option("Antibiotics"),
            ft.dropdown.Option("Maintenance"),
            ft.dropdown.Option("Diabetes"),
            ft.dropdown.Option("Heart Health"),
            ft.dropdown.Option("Vitamins"),
            ft.dropdown.Option("Antacid"),
            ft.dropdown.Option("Antidiarrheal"),
            ft.dropdown.Option("Antispasmodic"),
            ft.dropdown.Option("Probiotics"),
            ft.dropdown.Option("Antinausea"),
        ],
        value="All",
        width=200,
        border_color="primary", # dark mode fix
    )
    
    # container that holds all the results
    results_container = ft.Column(spacing=10)
    
    # helper for showing toast messages
    def show_snackbar(e, message, error=False):
        e.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor="error" if error else "primary",
        )
        e.page.snack_bar.open = True
        e.page.update()
    
    # logic to push items to the cart database
    def add_to_cart(medicine_id, medicine_name, e):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # creating table just in case it doesn't exist yet
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
            
            # check if we already have this item in the cart
            cursor.execute("""
                SELECT id, quantity FROM cart 
                WHERE patient_id = ? AND medicine_id = ?
            """, (user_id, medicine_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # if yes, just bump up the quantity
                cursor.execute("""
                    UPDATE cart 
                    SET quantity = quantity + 1 
                    WHERE id = ?
                """, (existing[0],))
                show_snackbar(e, f"Updated {medicine_name} quantity in cart")
            else:
                # if no, insert a new row
                cursor.execute("""
                    INSERT INTO cart (patient_id, medicine_id, quantity)
                    VALUES (?, ?, 1)
                """, (user_id, medicine_id))
                show_snackbar(e, f"Added {medicine_name} to cart")
            
            conn.commit()
            
            # notify the rest of the app that cart changed (updates sidebar)
            try:
                AppState.emit('cart_changed')
            except Exception:
                pass
            
        except Exception as ex:
            show_snackbar(e, f"Failed to add to cart: {str(ex)}", error=True)
        finally:
            conn.close()
    
    # this function used to show the details dialog
    # keeping it here in case we need it back later, but it's not used in the button anymore
    def view_medicine_details(med, e):
        dialog = ft.AlertDialog(
            title=ft.Text(med['name']),
            content=ft.Column([
                ft.Row([
                    ft.Text("Category:", weight="bold", width=100),
                    ft.Text(med['category']),
                ]),
                ft.Row([
                    ft.Text("Price:", weight="bold", width=100),
                    ft.Text(f"₱ {med['price']:.2f}", color="primary"),
                ]),
                ft.Row([
                    ft.Text("Stock:", weight="bold", width=100),
                    ft.Text(str(med['stock'])),
                ]),
                ft.Row([
                    ft.Text("Supplier:", weight="bold", width=100),
                    ft.Text(med['supplier']),
                ]),
                ft.Row([
                    ft.Text("Expiry:", weight="bold", width=100),
                    ft.Text(med['expiry_date']),
                ]),
            ], spacing=10, tight=True),
            actions=[
                ft.TextButton("Close", on_click=lambda e: close_dialog(e)),
                ft.ElevatedButton(
                    "Add to Cart",
                    icon=ft.Icons.ADD_SHOPPING_CART,
                    bgcolor="primary",
                    color="onPrimary",
                    on_click=lambda e: [
                        add_to_cart(med['id'], med['name'], e),
                        close_dialog(e)
                    ],
                    disabled=med['stock'] <= 0
                ),
            ],
        )
        
        e.page.dialog = dialog
        dialog.open = True
        e.page.update()
    
    # closes the dialog
    def close_dialog(e):
        e.page.dialog.open = False
        e.page.update()
    
    # creates the UI card for each medicine
    def create_medicine_card(med):
        return ft.Container(
            content=ft.Row([
                # medicine icon box
                ft.Container(
                    width=80,
                    height=80,
                    bgcolor="surfaceVariant",
                    border_radius=8,
                    content=ft.Icon(ft.Icons.MEDICATION, size=40, color="outline"),
                    alignment=ft.alignment.center,
                ),
                # medicine info
                ft.Column([
                ft.Text(med['name'], size=18, weight="bold"),
                ft.Text(f"Category: {med['category']}", size=13, color="outline"),
                ft.Row([
                    ft.Text(f"₱ {med['price']:.2f}", size=16, weight="bold", color="primary"),
                    # stock status badge
                    ft.Container(
                        content=ft.Text(
                            f"Stock: {med['stock']}" if med['stock'] > 0 else "Out of Stock",
                            size=12,
                            weight="bold",
                            color="onErrorContainer" if med['stock'] <= 0 else "onPrimaryContainer",
                        ),
                        bgcolor="errorContainer" if med['stock'] <= 0 else "primaryContainer",
                        border=ft.border.all(1, "primary"),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        border_radius=5,
                    ),
                ], spacing=10),
                ft.Text(f"Expires: {med['expiry_date']}", size=11, color="outline", italic=True),
            ], spacing=5, expand=True),
                
                # buttons section
                ft.Column([
                    # Add to Cart Button (Retained)
                    ft.IconButton(
                        icon=ft.Icons.ADD_SHOPPING_CART,
                        icon_color="onPrimary",
                        bgcolor="primary",
                        disabled=med['stock'] <= 0,
                        tooltip="Add to Cart",
                        on_click=lambda e, m_id=med['id'], m_name=med['name']: add_to_cart(m_id, m_name, e)
                    ),
                    # View Details Button REMOVED as requested
                ], spacing=5),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=15),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    # grabs the list of medicines from the DB
    def load_medicines(e=None):
        query = search_field.value.lower() if search_field.value else ""
        category = category_dropdown.value
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = "SELECT * FROM medicines WHERE 1=1"
        params = []
        
        # apply search filter
        if query:
            sql += " AND LOWER(name) LIKE ?"
            params.append(f"%{query}%")
        
        # apply category filter
        if category != "All":
            sql += " AND category = ?"
            params.append(category)
        
        sql += " ORDER BY name"
        
        cursor.execute(sql, params)
        medicines = cursor.fetchall()
        conn.close()
        
        # converting DB rows to dictionary so it's easier to use
        medicine_dicts = []
        for med in medicines:
            medicine_dicts.append({
                'id': med[0],
                'name': med[1],
                'category': med[2],
                'price': med[3],
                'stock': med[4],
                'expiry_date': med[5],
                'supplier': med[6],
            })
        
        results_container.controls.clear()
        
        if medicine_dicts:
            for med in medicine_dicts:
                results_container.controls.append(create_medicine_card(med))
        else:
            # empty state
            results_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF, size=80, color="outline"),
                        ft.Text("No medicines found", size=18, color="outline"),
                        ft.Text("Try a different search term or category", size=14, color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.alignment.center,
                )
            )
        
        if e:
            e.page.update()
    
    # Hack to load data on first start
    class FakePage:
        def update(self): pass
    load_medicines(type('Event', (), {'page': FakePage()})())
    
    # Main layout structure
    return ft.Column([
        ft.Text("Search Medicines", size=28, weight="bold"),
        ft.Text("Browse our available medicines and add them to your cart", size=14, color="outline"),
        
        ft.Container(height=20),
        
        # Search bar row
        ft.Row([
            search_field,
            category_dropdown,
            ft.ElevatedButton(
                "Search",
                icon=ft.Icons.SEARCH,
                on_click=load_medicines,
                bgcolor="primary",
                color="onPrimary",
                height=50,
            ),
        ], spacing=10),
        
        ft.Container(height=20),
        ft.Divider(),
        ft.Container(height=10),
        
        # Results list
        results_container,
    ], scroll=ft.ScrollMode.AUTO, spacing=0)