"""Medicine search and browse view."""

import flet as ft
from database import get_db_connection

def MedicineSearch():
    """Medicine search and browse view."""
    
    search_field = ft.TextField(
        hint_text="Search medicines by name...",
        prefix_icon=ft.Icons.SEARCH,
        border_color="outline",
        expand=True,
    )
    
    category_dropdown = ft.Dropdown(
        label="Category",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Pain Relief"),
            ft.dropdown.Option("Antibiotic"),
            ft.dropdown.Option("Supplement"),
        ],
        value="All",
        width=200,
    )
    
    results_container = ft.Column(spacing=10)
    
    def create_medicine_card(med):
        return ft.Container(
            content=ft.Row([
                # Medicine image placeholder
                ft.Container(
                    width=80,
                    height=80,
                    bgcolor="surfaceVariant",
                    border_radius=8,
                    content=ft.Icon(ft.Icons.MEDICATION, size=40, color="outline"),
                    alignment=ft.alignment.center,
                ),
                # Medicine details
                ft.Column([
                    ft.Text(med['name'], size=18, weight="bold"),
                    ft.Text(f"Category: {med['category']}", size=13, color="outline"),
                    ft.Row([
                        ft.Text(f"₱ {med['price']:.2f}", size=16, weight="bold", color="primary"),
                        ft.Container(
                            content=ft.Text(
                                f"Stock: {med['stock']}" if med['stock'] > 0 else "Out of Stock",
                                size=12,
                                weight="bold",
                                color="onErrorContainer" if med['stock'] <= 0 else "onPrimaryContainer",
                            ),
                            bgcolor="errorContainer" if med['stock'] <= 0 else "primaryContainer",
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=5,
                        ),
                    ], spacing=10),
                    ft.Text(f"Expires: {med['expiry_date']}", size=11, color="outline", italic=True),
                ], spacing=5, expand=True),
                # Add to cart button
                ft.Column([
                    ft.IconButton(
                        icon=ft.Icons.ADD_SHOPPING_CART,
                        icon_color="onPrimary",
                        bgcolor="primary",
                        disabled=med['stock'] <= 0,
                        tooltip="Add to Cart",
                    ),
                    ft.IconButton(
                        icon=ft.Icons.INFO_OUTLINE,
                        icon_color="primary",
                        tooltip="View Details",
                    ),
                ], spacing=5),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=15),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    def load_medicines(e=None):
        query = search_field.value.lower() if search_field.value else ""
        category = category_dropdown.value
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = "SELECT * FROM medicines WHERE 1=1"
        params = []
        
        if query:
            sql += " AND LOWER(name) LIKE ?"
            params.append(f"%{query}%")
        
        if category != "All":
            sql += " AND category = ?"
            params.append(category)
        
        cursor.execute(sql, params)
        medicines = cursor.fetchall()
        conn.close()
        
        results_container.controls.clear()
        
        if medicines:
            for med in medicines:
                results_container.controls.append(create_medicine_card(med))
        else:
            results_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF, size=80, color="outline"),
                        ft.Text("No medicines found", size=18, color="outline"),
                        ft.Text("Try a different search term", size=14, color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.alignment.center,
                )
            )
        
        if e:
            e.page.update()
    
    # Initial load
    class FakePage:
        def update(self): pass
    load_medicines(type('Event', (), {'page': FakePage()})())
    
    return ft.Column([
        ft.Text("Search Medicines", size=28, weight="bold"),
        ft.Text("Browse our available medicines and add them to your cart", size=14, color="outline"),
        
        ft.Container(height=20),
        
        # Search bar
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
        
        # Results
        results_container,
    ], scroll=ft.ScrollMode.AUTO, spacing=0)