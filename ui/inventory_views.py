import flet as ft
from database import get_db_connection

def InventoryDashboard():
    conn = get_db_connection()
    low_stock = conn.execute("SELECT * FROM medicines WHERE stock < 10").fetchall()
    total_meds = conn.execute("SELECT COUNT(*) FROM medicines").fetchone()[0]
    conn.close()

    alerts = [ft.Text("✅ System Healthy", color=ft.Colors.GREEN)]
    if low_stock:
        alerts = [ft.ListTile(leading=ft.Icon(ft.Icons.WARNING, color="error"), title=ft.Text(f"{m['name']} is low ({m['stock']})")) for m in low_stock] 

    return ft.Column([
        ft.Text("Inventory Overview", size=25, weight="bold"),
        
        ft.Row([
            ft.Container(
                expand=True, padding=20, bgcolor="tertiaryContainer", border_radius=10, 
                content=ft.Column([ft.Text("Total Products"), ft.Text(str(total_meds), size=30, weight="bold")])
            ),
            ft.Container(
                expand=True, padding=20, bgcolor="errorContainer", border_radius=10, 
                content=ft.Column([ft.Text("Low Stock Items"), ft.Text(str(len(low_stock)), size=30, weight="bold")])
            ),
        ]),

        ft.Divider(),
        ft.Text("Alerts & Notifications", size=18, weight="bold"),
        ft.Card(content=ft.Column(alerts))
    ])

def ManageStock():
    conn = get_db_connection()
    meds = conn.execute("SELECT * FROM medicines").fetchall()
    conn.close()

    dt = ft.DataTable(
        border=ft.border.all(1, "outline"), 
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, "outlineVariant"), 
        heading_row_color="surfaceVariant", 
        columns=[
            ft.DataColumn(ft.Text("Product Name")),
            ft.DataColumn(ft.Text("Category")),
            ft.DataColumn(ft.Text("Stock Level"), numeric=True),
            ft.DataColumn(ft.Text("Unit Price"), numeric=True),
            ft.DataColumn(ft.Text("Action")),
        ],
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(m['name'], weight="bold")),
                ft.DataCell(ft.Text(m['category'])),
                ft.DataCell(ft.Text(str(m['stock']), color=ft.Colors.RED if m['stock'] < 10 else ft.Colors.GREEN)),
                ft.DataCell(ft.Text(f"P{m['price']}")),
                ft.DataCell(ft.IconButton(ft.Icons.EDIT, tooltip="Edit Stock")),
            ]) for m in meds
        ]
    )
    return ft.Column([
        ft.Row([
            ft.Text("Stock Management", size=20, weight="bold"),
            ft.ElevatedButton("Add New Product", icon=ft.Icons.ADD)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        dt
    ], scroll=ft.ScrollMode.AUTO)