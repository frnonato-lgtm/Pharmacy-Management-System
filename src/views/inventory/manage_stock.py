import flet as ft
from services.database import get_db_connection

def ManageStock():
    """Table to view and add medicines."""
    
    # Define the table structure
    stock_table = ft.DataTable(
        border=ft.border.all(1, "outline"),
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, "outlineVariant"),
        heading_row_color="surfaceVariant",
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("Category")),
            ft.DataColumn(ft.Text("Stock"), numeric=True),
            ft.DataColumn(ft.Text("Price"), numeric=True),
            ft.DataColumn(ft.Text("Expiry")),
        ],
        rows=[]
    )

    # Function to get data from DB
    def load_data():
        conn = get_db_connection()
        meds = conn.execute("SELECT * FROM medicines").fetchall()
        conn.close()

        stock_table.rows.clear()
        for m in meds:
            # Make text red if stock is low
            stock_color = "error" if m['stock'] < 10 else "onSurface"
            
            stock_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(m['id']))),
                    ft.DataCell(ft.Text(m['name'], weight="bold")),
                    ft.DataCell(ft.Text(m['category'])),
                    ft.DataCell(ft.Text(str(m['stock']), color=stock_color, weight="bold")),
                    ft.DataCell(ft.Text(f"P{m['price']:.2f}")),
                    ft.DataCell(ft.Text(m['expiry_date'])),
                ])
            )

    load_data() # Run on start

    # Pop-up dialog to add new medicine
    def add_medicine_dialog(e):
        name = ft.TextField(label="Name")
        category = ft.Dropdown(label="Category", options=[
            ft.dropdown.Option("Antibiotic"), ft.dropdown.Option("Pain Relief"), ft.dropdown.Option("Supplement")
        ])
        price = ft.TextField(label="Price", keyboard_type="number")
        stock = ft.TextField(label="Stock", keyboard_type="number")
        expiry = ft.TextField(label="Expiry (YYYY-MM-DD)")

        def save_med(e):
            if not name.value or not price.value: return 
            
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO medicines (name, category, price, stock, expiry_date) VALUES (?, ?, ?, ?, ?)",
                (name.value, category.value, float(price.value), int(stock.value), expiry.value)
            )
            conn.commit()
            conn.close()
            dlg.open = False
            load_data() 
            e.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Add Medicine"),
            content=ft.Column([name, category, price, stock, expiry], tight=True, width=400),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: (setattr(dlg, 'open', False), e.page.update())),
                ft.ElevatedButton("Save", on_click=save_med),
            ]
        )
        e.page.dialog = dlg
        dlg.open = True
        e.page.update()

    return ft.Column([
        ft.Row([
            ft.Text("Stock Management", size=28, weight="bold"),
            ft.ElevatedButton("Refresh", icon=ft.Icons.REFRESH, on_click=lambda e: (load_data(), e.page.update())),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        ft.Container(height=10),
        
        ft.Row([
            ft.ElevatedButton("Add Medicine", icon=ft.Icons.ADD, bgcolor="primary", color="onPrimary", on_click=add_medicine_dialog),
        ]),
        
        ft.Container(height=20),
        ft.Column([stock_table], scroll=ft.ScrollMode.AUTO, expand=True)
        
    ], scroll=ft.ScrollMode.AUTO, expand=True)