import flet as ft
from services.database import get_db_connection
from datetime import datetime

def ManageStock():
    """Page to Add, Update, Delete, and Search Medicines."""
    
    # Variable to track if we are editing an existing medicine or adding a new one
    # If None, we are adding. If it has a number, we are editing that ID.
    selected_medicine_id = None 
    
    # --- HELPER FUNCTIONS ---
    
    # I made this function so I don't have to type the same style properties over and over for every text field
    def create_input(label, icon=None, numeric=False, expand=False):
        return ft.TextField(
            label=label,
            prefix_icon=icon,
            # If numeric is True, show number keyboard, otherwise text
            keyboard_type=ft.KeyboardType.NUMBER if numeric else ft.KeyboardType.TEXT,
            height=45, 
            text_size=13,
            border_color="outline",
            focused_border_color="primary",
            content_padding=10,
            expand=expand # This lets the field stretch if needed
        )

    # --- UI COMPONENTS ---
    
    # Search bar at the top
    search_txt = ft.TextField(
        hint_text="Search medicine name...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        height=45,
        content_padding=10,
        on_submit=lambda e: load_data() # Search when Enter is pressed
    )
    
    # Dropdown to filter by category
    category_filter = ft.Dropdown(
        label="Category",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Pain Relief"),
            ft.dropdown.Option("Antibiotics"),
            ft.dropdown.Option("Cough & Cold"),
            ft.dropdown.Option("Vitamins"),
            ft.dropdown.Option("Maintenance"),
            ft.dropdown.Option("Diabetes"),
            ft.dropdown.Option("Heart Health"),
            ft.dropdown.Option("Antacid"),
            ft.dropdown.Option("Antidiarrheal"),
            ft.dropdown.Option("Supplements"),
        ],
        value="All",
        width=200,
        content_padding=10,
        on_change=lambda e: load_data() # Refresh table when changed
    )
    
    # Dropdown to filter by stock level
    stock_filter = ft.Dropdown(
        label="Stock Status",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Low Stock"),   
            ft.dropdown.Option("Out of Stock"), 
            ft.dropdown.Option("Good Stock"),   
        ],
        value="All",
        width=150,
        content_padding=10,
        on_change=lambda e: load_data()
    )

    # --- INPUT FIELDS FOR THE POPUP DIALOG ---
    
    name_input = create_input("Medicine Name", ft.Icons.MEDICATION)
    
    # For the category inside the Add/Edit form, we copy options from the filter but remove "All"
    category_input = ft.Dropdown(
        label="Category",
        options=category_filter.options[1:], 
        content_padding=10,
        border_color="outline",
        focused_border_color="primary"
    )
    
    # Price and Stock inputs (will be side-by-side)
    price_input = create_input("Price (PHP)", None, numeric=True, expand=True)
    stock_input = create_input("Stock Qty", None, numeric=True, expand=True)
    
    expiry_input = create_input("Expiry (YYYY-MM-DD)", ft.Icons.CALENDAR_TODAY)
    supplier_input = create_input("Supplier", ft.Icons.LOCAL_SHIPPING)

    # The main table to show data
    stock_table = ft.DataTable(
        border=ft.border.all(1, "outline"),
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, "outlineVariant"),
        heading_row_color="surfaceVariant",
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("Category")),
            ft.DataColumn(ft.Text("Price"), numeric=True),
            ft.DataColumn(ft.Text("Stock"), numeric=True),
            ft.DataColumn(ft.Text("Expiry")),
            ft.DataColumn(ft.Text("Supplier")),
            ft.DataColumn(ft.Text("Actions")),
        ],
        rows=[]
    )

    # --- APP LOGIC ---

    # This function connects to the DB and fills the table based on filters
    def load_data():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base query
        query = "SELECT * FROM medicines WHERE 1=1"
        params = []

        # Add filters if they are set
        if search_txt.value:
            query += " AND name LIKE ?"
            params.append(f"%{search_txt.value}%")
        
        if category_filter.value != "All":
            query += " AND category = ?"
            params.append(category_filter.value)
            
        if stock_filter.value == "Low Stock":
            query += " AND stock > 0 AND stock < 10"
        elif stock_filter.value == "Out of Stock":
            query += " AND stock = 0"
        elif stock_filter.value == "Good Stock":
            query += " AND stock >= 10"

        # Make sure it's sorted by ID (1, 2, 3...)
        query += " ORDER BY id ASC"

        cursor.execute(query, params)
        meds = cursor.fetchall()
        conn.close()

        # Clear old rows
        stock_table.rows.clear()
        
        # Loop through data and add rows to the table
        for m in meds:
            # Color code the stock number: Red = Empty, Orange = Low, Blue = Good
            if m['stock'] == 0:
                stock_color = "error"
            elif m['stock'] < 10:
                stock_color = "orange"
            else:
                stock_color = "primary"

            stock_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(m['id']))),
                    ft.DataCell(ft.Text(m['name'], weight="bold")),
                    ft.DataCell(ft.Text(m['category'])),
                    ft.DataCell(ft.Text(f"₱{m['price']:.2f}")),
                    ft.DataCell(ft.Text(str(m['stock']), color=stock_color, weight="bold")),
                    ft.DataCell(ft.Text(m['expiry_date'])),
                    ft.DataCell(ft.Text(m['supplier'] or "N/A")),
                    # Add Edit and Delete buttons for each row
                    ft.DataCell(ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.EDIT, 
                            icon_color="primary", 
                            tooltip="Edit",
                            on_click=lambda e, med=m: open_edit_dialog(med)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE, 
                            icon_color="error", 
                            tooltip="Delete",
                            on_click=lambda e, med_id=m['id']: open_delete_dialog(e, med_id)
                        ),
                    ])),
                ])
            )
        
        # Update the UI only if the table is visible
        if stock_table.page:
            stock_table.update()

    # Prepares the dialog for adding a NEW medicine
    def open_add_dialog(e):
        nonlocal selected_medicine_id
        selected_medicine_id = None # None means we are adding, not editing
        
        # Clear all input fields
        name_input.value = ""
        category_input.value = None
        price_input.value = ""
        stock_input.value = ""
        expiry_input.value = ""
        supplier_input.value = ""
        
        dialog.title = ft.Text("Add New Medicine")
        dialog.open = True
        e.page.update()

    # Prepares the dialog for EDITING an existing medicine
    def open_edit_dialog(med):
        nonlocal selected_medicine_id
        selected_medicine_id = med['id'] # Remember which ID we are editing
        
        # Fill the boxes with the current data
        name_input.value = med['name']
        category_input.value = med['category']
        price_input.value = str(med['price'])
        stock_input.value = str(med['stock'])
        expiry_input.value = med['expiry_date']
        supplier_input.value = med['supplier']
        
        dialog.title = ft.Text("Edit Medicine")
        dialog.open = True
        if name_input.page:
            name_input.page.update()

    # Saves the data to the database
    def save_medicine(e):
        # Basic check to make sure fields aren't empty
        if not name_input.value or not price_input.value or not stock_input.value:
            e.page.snack_bar = ft.SnackBar(ft.Text("Please fill in Name, Price, and Stock!"), bgcolor="error")
            e.page.snack_bar.open = True
            e.page.update()
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            if selected_medicine_id is None:
                # INSERT new record
                cursor.execute("""
                    INSERT INTO medicines (name, category, price, stock, expiry_date, supplier) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    name_input.value, 
                    category_input.value, 
                    float(price_input.value), 
                    int(stock_input.value), 
                    expiry_input.value, 
                    supplier_input.value
                ))
                msg = "Medicine Added Successfully!"
            else:
                # UPDATE existing record
                cursor.execute("""
                    UPDATE medicines 
                    SET name=?, category=?, price=?, stock=?, expiry_date=?, supplier=?
                    WHERE id=?
                """, (
                    name_input.value, 
                    category_input.value, 
                    float(price_input.value), 
                    int(stock_input.value), 
                    expiry_input.value, 
                    supplier_input.value,
                    selected_medicine_id
                ))
                msg = "Medicine Updated Successfully!"

            conn.commit()
            conn.close()
            
            # Close popup and refresh the list
            dialog.open = False
            load_data()
            
            e.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor="green")
            e.page.snack_bar.open = True
            e.page.update()

        except Exception as ex:
            e.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor="error")
            e.page.snack_bar.open = True
            e.page.update()

    # Shows a confirmation popup before deleting
    def open_delete_dialog(e, med_id):
        def confirm_delete(e):
            conn = get_db_connection()
            conn.execute("DELETE FROM medicines WHERE id = ?", (med_id,))
            conn.commit()
            conn.close()
            
            del_dialog.open = False
            load_data()
            e.page.snack_bar = ft.SnackBar(ft.Text("Medicine Deleted!"), bgcolor="error")
            e.page.snack_bar.open = True
            e.page.update()

        del_dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text("Are you sure you want to delete this medicine?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(del_dialog, 'open', False) or e.page.update()),
                ft.ElevatedButton("Delete", bgcolor="error", color="white", on_click=confirm_delete),
            ]
        )
        e.page.dialog = del_dialog
        del_dialog.open = True
        e.page.update()

    # --- DEFINE DIALOGS ---
    
    # The main form dialog
    dialog = ft.AlertDialog(
        content=ft.Container(
            width=450,
            # Use Column to stack fields, and Row to put Price/Stock side-by-side
            content=ft.Column([
                name_input,
                ft.Container(height=5),
                category_input,
                ft.Container(height=5),
                ft.Row([price_input, stock_input], spacing=15),
                ft.Container(height=5),
                expiry_input,
                ft.Container(height=5),
                supplier_input
            ], tight=True)
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, 'open', False) or e.page.update()),
            ft.ElevatedButton("Save", bgcolor="primary", color="onPrimary", on_click=save_medicine),
        ]
    )

    # Run this once when page loads to fill the table
    load_data()

    # --- MAIN PAGE LAYOUT ---
    return ft.Column([
        # Header Row
        ft.Row([
            ft.Text("Stock Management", size=28, weight="bold"),
            ft.Row([
                ft.ElevatedButton("Refresh", icon=ft.Icons.REFRESH, on_click=lambda e: (load_data(), e.page.update())),
                ft.ElevatedButton("Add Medicine", icon=ft.Icons.ADD, bgcolor="primary", color="onPrimary", on_click=open_add_dialog),
            ])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        ft.Container(height=10),
        
        # Filter Bar
        ft.Container(
            content=ft.Row([
                search_txt,
                category_filter,
                stock_filter,
                ft.IconButton(icon=ft.Icons.SEARCH, icon_color="primary", on_click=lambda e: load_data())
            ], spacing=10),
            padding=15,
            bgcolor="surfaceVariant",
            border_radius=10
        ),
        
        ft.Container(height=20),
        
        # Table Container (with horizontal scrolling enabled)
        ft.Column([
            ft.Row([stock_table], scroll=ft.ScrollMode.AUTO)
        ], scroll=ft.ScrollMode.AUTO, expand=True),
        
        # Include dialogs here so they can be shown
        dialog 
        
    ], scroll=ft.ScrollMode.AUTO, expand=True)