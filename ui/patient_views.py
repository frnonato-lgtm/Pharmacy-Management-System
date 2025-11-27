import flet as ft
from database import get_db_connection

def PatientDashboard():
    return ft.Column([
        ft.Text("Patient Overview", size=25, weight="bold"),
        ft.Row([
            ft.Container(
                padding=20, bgcolor="primaryContainer", border_radius=10, expand=True, 
                content=ft.Column([
                    ft.Icon(ft.Icons.SHOPPING_CART, size=30, color="primary"), 
                    ft.Text("Active Orders", size=12),
                    ft.Text("2 Items", size=20, weight="bold")
                ])
            ),
            ft.Container(
                padding=20, bgcolor="secondaryContainer", border_radius=10, expand=True, 
                content=ft.Column([
                    ft.Icon(ft.Icons.HISTORY, size=30, color="secondary"), 
                    ft.Text("Last Visit", size=12),
                    ft.Text("Nov 24", size=20, weight="bold")
                ])
            ),
        ]),
        ft.Divider(),
        ft.Text("Recommended for you", size=16, weight="bold"),
        ft.Container(height=100, bgcolor="surfaceVariant", border_radius=10, alignment=ft.alignment.center, content=ft.Text("No recommendations yet")) 
    ])

def MedicineSearch():
    conn = get_db_connection()
    meds = conn.execute("SELECT * FROM medicines").fetchall()
    conn.close()

    grid = ft.GridView(
        expand=True, runs_count=4, max_extent=250, child_aspect_ratio=0.8,
        spacing=10, run_spacing=10,
    )

    for med in meds:
        stock_color = ft.Colors.GREEN if med['stock'] > 10 else ft.Colors.RED
        
        grid.controls.append(
            ft.Container(
                bgcolor="surfaceVariant", 
                border_radius=10,
                padding=15,
                content=ft.Column([
                    ft.Icon(ft.Icons.MEDICATION, size=40, color="primary"), 
                    ft.Text(med['name'], weight="bold", size=16),
                    ft.Text(med['category'], size=12, italic=True),
                    ft.Divider(),
                    ft.Row([
                        ft.Text(f"P{med['price']}", weight="bold", size=18),
                        ft.Text(f"Stock: {med['stock']}", color=stock_color, size=12),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.ElevatedButton("Add to Cart", width=150)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        )

    return ft.Column([
        ft.Text("Search Medicines", size=20, weight="bold"),
        ft.TextField(prefix_icon=ft.Icons.SEARCH, hint_text="Type medicine name..."),
        ft.Divider(),
        ft.Container(content=grid, expand=True)
    ], expand=True)

def CartView():
    return ft.Column([
        ft.Text("My Shopping Cart", size=25, weight="bold"),
        ft.Container(
            padding=20,
            border=ft.border.all(1, "outline"), 
            border_radius=10,
            content=ft.Column([
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.MEDICATION, color="primary"), 
                    title=ft.Text("Paracetamol"),
                    subtitle=ft.Text("500mg - 2 packs"),
                    trailing=ft.Text("P 10.00", weight="bold")
                ),
                ft.Divider(),
                ft.Row([
                    ft.Text("Total Amount:", weight="bold"),
                    ft.Text("P 10.00", weight="bold", size=20, color="primary") 
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.ElevatedButton("Checkout Now", width=200, bgcolor="primary", color="onPrimary") 
            ])
        )
    ])