import flet as ft

def BillingDashboard():
    return ft.Column([
        ft.Text("Financial Overview", size=25, weight="bold"),
        
        ft.Row([
            ft.Container(
                expand=True, padding=20, bgcolor="primaryContainer", border_radius=10, 
                content=ft.Column([ft.Text("Today's Sales"), ft.Text("P 12,500.00", size=25, weight="bold", color="onPrimaryContainer")]) 
            ),
            ft.Container(
                expand=True, padding=20, bgcolor="secondaryContainer", border_radius=10, 
                content=ft.Column([ft.Text("Pending Invoices"), ft.Text("3", size=25, weight="bold", color="onSecondaryContainer")]) 
            ),
        ]),

        ft.Divider(),
        ft.Text("Recent Transactions", size=20, weight="bold"),
        
        ft.DataTable(
            heading_row_color="surfaceVariant", 
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Customer")),
                ft.DataColumn(ft.Text("Amount")),
                ft.DataColumn(ft.Text("Status")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("#1011")),
                    ft.DataCell(ft.Text("Jane Doe")),
                    ft.DataCell(ft.Text("P 500.00")),
                    ft.DataCell(ft.Container(content=ft.Text("PAID", size=10, color="white"), bgcolor="green", padding=5, border_radius=5)),
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("#1010")),
                    ft.DataCell(ft.Text("John Smith")),
                    ft.DataCell(ft.Text("P 1,200.00")),
                    ft.DataCell(ft.Container(content=ft.Text("PENDING", size=10, color="white"), bgcolor="orange", padding=5, border_radius=5)),
                ]),
            ]
        )
    ], scroll=ft.ScrollMode.AUTO)

def InvoicesView():
    return ft.Column([
        ft.Text("Invoice Generation", size=25, weight="bold"),
        ft.TextField(label="Enter Patient ID or Name", prefix_icon=ft.Icons.SEARCH),
        ft.ElevatedButton("Create New Invoice", icon=ft.Icons.ADD)
    ])