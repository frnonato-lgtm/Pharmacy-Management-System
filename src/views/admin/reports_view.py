"""System reports generation and viewing."""

import flet as ft
from services.database import get_db_connection
from datetime import datetime, timedelta

def ReportsView():
    """Reports interface for administrators."""
    
    report_output = ft.Column(spacing=10)
    
    # Report type selector
    report_type = ft.Dropdown(
        label="Report Type",
        options=[
            ft.dropdown.Option("user_activity", "User Activity Report"),
            ft.dropdown.Option("inventory_status", "Inventory Status Report"),
            ft.dropdown.Option("prescription_summary", "Prescription Summary"),
            ft.dropdown.Option("low_stock", "Low Stock Alert Report"),
            ft.dropdown.Option("system_usage", "System Usage Statistics"),
        ],
        value="user_activity",
        width=300,
    )
    
    # Date range
    date_from = ft.TextField(
        label="From Date",
        hint_text="YYYY-MM-DD",
        value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        width=200,
    )
    
    date_to = ft.TextField(
        label="To Date",
        hint_text="YYYY-MM-DD",
        value=datetime.now().strftime("%Y-%m-%d"),
        width=200,
    )
    
    def generate_user_activity_report():
        """Generate user activity report."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user counts by role
        cursor.execute("""
            SELECT role, COUNT(*) as count
            FROM users
            GROUP BY role
            ORDER BY count DESC
        """)
        role_stats = cursor.fetchall()
        
        # Get recent registrations
        cursor.execute("""
            SELECT username, full_name, role, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 10
        """)
        recent_users = cursor.fetchall()
        
        conn.close()
        
        # Build report
        controls = [
            ft.Text("User Activity Report", size=24, weight="bold"),
            ft.Text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                   size=12, color="outline"),
            ft.Divider(height=20),
            
            # Role statistics
            ft.Text("Users by Role", size=18, weight="bold"),
            ft.Container(height=10),
        ]
        
        # Role stats table
        for role_stat in role_stats:
            controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PEOPLE, color="primary", size=20),
                        ft.Text(role_stat['role'], size=14, weight="bold", expand=1),
                        ft.Text(f"{role_stat['count']} users", size=14),
                    ], spacing=10),
                    padding=10,
                    border=ft.border.all(1, "outlineVariant"),
                    border_radius=8,
                )
            )
        
        controls.extend([
            ft.Container(height=20),
            ft.Text("Recent Registrations", size=18, weight="bold"),
            ft.Container(height=10),
        ])
        
        # Recent users table
        if recent_users:
            controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text("Username", size=12, weight="bold", expand=1),
                        ft.Text("Full Name", size=12, weight="bold", expand=2),
                        ft.Text("Role", size=12, weight="bold", expand=1),
                        ft.Text("Registered", size=12, weight="bold", expand=1),
                    ]),
                    bgcolor="surfaceVariant",
                    padding=10,
                    border_radius=8,
                )
            )
            
            for user in recent_users:
                controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(user['username'], size=12, expand=1),
                            ft.Text(user['full_name'], size=12, expand=2),
                            ft.Text(user['role'], size=12, expand=1),
                            ft.Text(user['created_at'][:10] if user['created_at'] else "N/A", 
                                   size=12, expand=1),
                        ]),
                        padding=10,
                        border=ft.border.all(1, "outlineVariant"),
                        border_radius=8,
                    )
                )
        
        return controls
    
    def generate_inventory_report():
        """Generate inventory status report."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get inventory statistics
        cursor.execute("SELECT COUNT(*) as total FROM medicines")
        total_meds = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as low_stock FROM medicines WHERE stock < 10")
        low_stock = cursor.fetchone()['low_stock']
        
        cursor.execute("SELECT COUNT(*) as out_of_stock FROM medicines WHERE stock = 0")
        out_of_stock = cursor.fetchone()['out_of_stock']
        
        cursor.execute("SELECT SUM(stock * price) as total_value FROM medicines")
        total_value = cursor.fetchone()['total_value'] or 0
        
        # Get medicines by category
        cursor.execute("""
            SELECT category, COUNT(*) as count, SUM(stock) as total_stock
            FROM medicines
            GROUP BY category
            ORDER BY count DESC
        """)
        categories = cursor.fetchall()
        
        # Get top 10 medicines by stock
        cursor.execute("""
            SELECT name, category, stock, price, (stock * price) as value
            FROM medicines
            ORDER BY stock DESC
            LIMIT 10
        """)
        top_stock = cursor.fetchall()
        
        conn.close()
        
        # Build report
        controls = [
            ft.Text("Inventory Status Report", size=24, weight="bold"),
            ft.Text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                   size=12, color="outline"),
            ft.Divider(height=20),
            
            # Summary cards
            ft.Row([
                create_summary_card("Total Medicines", total_meds, ft.Icons.MEDICATION, "primary"),
                create_summary_card("Low Stock", low_stock, ft.Icons.WARNING, "error"),
                create_summary_card("Out of Stock", out_of_stock, ft.Icons.ERROR, "error"),
                create_summary_card(f"Total Value", f"₱{total_value:,.2f}", ft.Icons.PAYMENTS, "secondary"),
            ], spacing=10, wrap=True),
            
            ft.Container(height=20),
            ft.Text("Inventory by Category", size=18, weight="bold"),
            ft.Container(height=10),
        ]
        
        # Category breakdown
        for cat in categories:
            controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CATEGORY, color="secondary", size=20),
                        ft.Text(cat['category'], size=14, weight="bold", expand=1),
                        ft.Text(f"{cat['count']} items", size=14),
                        ft.Text(f"Stock: {cat['total_stock']}", size=14),
                    ], spacing=10),
                    padding=10,
                    border=ft.border.all(1, "outlineVariant"),
                    border_radius=8,
                )
            )
        
        controls.extend([
            ft.Container(height=20),
            ft.Text("Top 10 Items by Stock", size=18, weight="bold"),
            ft.Container(height=10),
        ])
        
        # Top stock items
        if top_stock:
            controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text("Medicine", size=12, weight="bold", expand=2),
                        ft.Text("Category", size=12, weight="bold", expand=1),
                        ft.Text("Stock", size=12, weight="bold", expand=1),
                        ft.Text("Price", size=12, weight="bold", expand=1),
                        ft.Text("Value", size=12, weight="bold", expand=1),
                    ]),
                    bgcolor="surfaceVariant",
                    padding=10,
                    border_radius=8,
                )
            )
            
            for med in top_stock:
                controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(med['name'], size=12, expand=2),
                            ft.Text(med['category'], size=12, expand=1),
                            ft.Text(str(med['stock']), size=12, expand=1),
                            ft.Text(f"₱{med['price']:.2f}", size=12, expand=1),
                            ft.Text(f"₱{med['value']:.2f}", size=12, expand=1),
                        ]),
                        padding=10,
                        border=ft.border.all(1, "outlineVariant"),
                        border_radius=8,
                    )
                )
        
        return controls
    
    def generate_prescription_report():
        """Generate prescription summary report."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get prescription statistics
        cursor.execute("SELECT COUNT(*) as total FROM prescriptions")
        total_rx = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as pending FROM prescriptions WHERE status = 'Pending'")
        pending = cursor.fetchone()['pending']
        
        cursor.execute("SELECT COUNT(*) as approved FROM prescriptions WHERE status = 'Approved'")
        approved = cursor.fetchone()['approved']
        
        cursor.execute("SELECT COUNT(*) as rejected FROM prescriptions WHERE status = 'Rejected'")
        rejected = cursor.fetchone()['rejected']
        
        # Get recent prescriptions
        cursor.execute("""
            SELECT p.id, p.status, p.created_at, u.full_name as patient_name
            FROM prescriptions p
            JOIN users u ON p.patient_id = u.id
            ORDER BY p.created_at DESC
            LIMIT 15
        """)
        recent_rx = cursor.fetchall()
        
        conn.close()
        
        # Build report
        controls = [
            ft.Text("Prescription Summary Report", size=24, weight="bold"),
            ft.Text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                   size=12, color="outline"),
            ft.Divider(height=20),
            
            # Summary cards
            ft.Row([
                create_summary_card("Total Prescriptions", total_rx, ft.Icons.DESCRIPTION, "primary"),
                create_summary_card("Pending", pending, ft.Icons.PENDING, "tertiary"),
                create_summary_card("Approved", approved, ft.Icons.CHECK_CIRCLE, "primary"),
                create_summary_card("Rejected", rejected, ft.Icons.CANCEL, "error"),
            ], spacing=10, wrap=True),
            
            ft.Container(height=20),
            ft.Text("Recent Prescriptions", size=18, weight="bold"),
            ft.Container(height=10),
        ]
        
        # Recent prescriptions table
        if recent_rx:
            controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text("ID", size=12, weight="bold", expand=1),
                        ft.Text("Patient", size=12, weight="bold", expand=2),
                        ft.Text("Status", size=12, weight="bold", expand=1),
                        ft.Text("Date", size=12, weight="bold", expand=1),
                    ]),
                    bgcolor="surfaceVariant",
                    padding=10,
                    border_radius=8,
                )
            )
            
            for rx in recent_rx:
                status_color = {
                    "Pending": "tertiary",
                    "Approved": "primary",
                    "Rejected": "error"
                }.get(rx['status'], "outline")
                
                controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(f"#{rx['id']}", size=12, expand=1),
                            ft.Text(rx['patient_name'], size=12, expand=2),
                            ft.Container(
                                content=ft.Text(rx['status'], size=11, color=f"on{status_color.capitalize()}"),
                                bgcolor=ft.Colors.with_opacity(0.2, status_color),
                                padding=5,
                                border_radius=5,
                                expand=1,
                            ),
                            ft.Text(rx['created_at'][:10] if rx['created_at'] else "N/A", 
                                   size=12, expand=1),
                        ]),
                        padding=10,
                        border=ft.border.all(1, "outlineVariant"),
                        border_radius=8,
                    )
                )
        
        return controls
    
    def generate_low_stock_report():
        """Generate low stock alert report."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get low stock items
        cursor.execute("""
            SELECT name, category, stock, price, supplier
            FROM medicines
            WHERE stock < 10
            ORDER BY stock ASC
        """)
        low_stock_items = cursor.fetchall()
        
        # Get out of stock items
        cursor.execute("""
            SELECT name, category, price, supplier
            FROM medicines
            WHERE stock = 0
            ORDER BY name
        """)
        out_of_stock_items = cursor.fetchall()
        
        conn.close()
        
        # Build report
        controls = [
            ft.Text("Low Stock Alert Report", size=24, weight="bold"),
            ft.Text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                   size=12, color="outline"),
            ft.Divider(height=20),
        ]
        
        # Out of stock section
        if out_of_stock_items:
            controls.extend([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ERROR, color="error", size=30),
                        ft.Text(f"{len(out_of_stock_items)} items are OUT OF STOCK!", 
                               size=16, weight="bold", color="error"),
                    ], spacing=10),
                    bgcolor=ft.Colors.with_opacity(0.1, "error"),
                    padding=15,
                    border_radius=8,
                ),
                ft.Container(height=10),
                
                ft.Container(
                    content=ft.Row([
                        ft.Text("Medicine", size=12, weight="bold", expand=2),
                        ft.Text("Category", size=12, weight="bold", expand=1),
                        ft.Text("Price", size=12, weight="bold", expand=1),
                        ft.Text("Supplier", size=12, weight="bold", expand=2),
                    ]),
                    bgcolor="surfaceVariant",
                    padding=10,
                    border_radius=8,
                ),
            ])
            
            for item in out_of_stock_items:
                controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(item['name'], size=12, expand=2),
                            ft.Text(item['category'], size=12, expand=1),
                            ft.Text(f"₱{item['price']:.2f}", size=12, expand=1),
                            ft.Text(item['supplier'] or "N/A", size=12, expand=2),
                        ]),
                        padding=10,
                        border=ft.border.all(1, "error"),
                        border_radius=8,
                        bgcolor=ft.Colors.with_opacity(0.05, "error"),
                    )
                )
            
            controls.append(ft.Container(height=20))
        
        # Low stock section
        if low_stock_items:
            controls.extend([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.WARNING, color="tertiary", size=30),
                        ft.Text(f"{len(low_stock_items)} items have LOW STOCK (< 10 units)", 
                               size=16, weight="bold", color="tertiary"),
                    ], spacing=10),
                    bgcolor=ft.Colors.with_opacity(0.1, "tertiary"),
                    padding=15,
                    border_radius=8,
                ),
                ft.Container(height=10),
                
                ft.Container(
                    content=ft.Row([
                        ft.Text("Medicine", size=12, weight="bold", expand=2),
                        ft.Text("Category", size=12, weight="bold", expand=1),
                        ft.Text("Stock", size=12, weight="bold", expand=1),
                        ft.Text("Price", size=12, weight="bold", expand=1),
                        ft.Text("Supplier", size=12, weight="bold", expand=2),
                    ]),
                    bgcolor="surfaceVariant",
                    padding=10,
                    border_radius=8,
                ),
            ])
            
            for item in low_stock_items:
                controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(item['name'], size=12, expand=2),
                            ft.Text(item['category'], size=12, expand=1),
                            ft.Text(str(item['stock']), size=12, weight="bold", 
                                   color="tertiary", expand=1),
                            ft.Text(f"₱{item['price']:.2f}", size=12, expand=1),
                            ft.Text(item['supplier'] or "N/A", size=12, expand=2),
                        ]),
                        padding=10,
                        border=ft.border.all(1, "outlineVariant"),
                        border_radius=8,
                    )
                )
        
        if not low_stock_items and not out_of_stock_items:
            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="primary", size=50),
                        ft.Text("All inventory levels are healthy!", 
                               size=18, weight="bold", color="primary"),
                    ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=50,
                )
            )
        
        return controls
    
    def generate_system_usage_report():
        """Generate system usage statistics."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get various counts
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM medicines")
        total_medicines = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM prescriptions")
        total_prescriptions = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM invoices")
        total_invoices = cursor.fetchone()['count']
        
        # Get users by role
        cursor.execute("""
            SELECT role, COUNT(*) as count
            FROM users
            GROUP BY role
        """)
        users_by_role = cursor.fetchall()
        
        conn.close()
        
        # Build report
        controls = [
            ft.Text("System Usage Statistics", size=24, weight="bold"),
            ft.Text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                   size=12, color="outline"),
            ft.Divider(height=20),
            
            ft.Text("Overall System Statistics", size=18, weight="bold"),
            ft.Container(height=10),
            
            ft.Row([
                create_summary_card("Total Users", total_users, ft.Icons.PEOPLE, "primary"),
                create_summary_card("Total Medicines", total_medicines, ft.Icons.MEDICATION, "secondary"),
                create_summary_card("Prescriptions", total_prescriptions, ft.Icons.DESCRIPTION, "tertiary"),
                create_summary_card("Invoices", total_invoices, ft.Icons.RECEIPT, "primary"),
            ], spacing=10, wrap=True),
            
            ft.Container(height=20),
            ft.Text("User Distribution", size=18, weight="bold"),
            ft.Container(height=10),
        ]
        
        # User role distribution
        for role_data in users_by_role:
            percentage = (role_data['count'] / total_users * 100) if total_users > 0 else 0
            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(role_data['role'], size=14, weight="bold", expand=1),
                            ft.Text(f"{role_data['count']} users ({percentage:.1f}%)", size=14),
                        ]),
                        ft.ProgressBar(
                            value=percentage / 100,
                            color="primary",
                            bgcolor="surfaceVariant",
                        ),
                    ], spacing=5),
                    padding=15,
                    border=ft.border.all(1, "outlineVariant"),
                    border_radius=8,
                )
            )
        
        return controls
    
    def create_summary_card(title, value, icon, color):
        """Helper to create summary cards."""
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=30),
                ft.Text(str(value), size=24, weight="bold", color=color),
                ft.Text(title, size=12, color="outline"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
            expand=True,
        )
    
    def generate_report(e):
        """Generate selected report."""
        report_output.controls.clear()
        
        report_generators = {
            "user_activity": generate_user_activity_report,
            "inventory_status": generate_inventory_report,
            "prescription_summary": generate_prescription_report,
            "low_stock": generate_low_stock_report,
            "system_usage": generate_system_usage_report,
        }
        
        generator = report_generators.get(report_type.value)
        if generator:
            report_output.controls = generator()
        
        e.page.update()
    
    def export_report(e):
        """Export report to file (placeholder)."""
        e.page.snack_bar = ft.SnackBar(
            content=ft.Text("Export feature coming soon!"),
            bgcolor="secondary",
        )
        e.page.snack_bar.open = True
        e.page.update()
    
    return ft.Column([
        ft.Row([
            ft.Text("System Reports", size=28, weight="bold"),
        ]),
        ft.Text("Generate and view system reports", size=14, color="outline"),
        
        ft.Container(height=20),
        
        # Report controls
        ft.Container(
            content=ft.Column([
                ft.Row([
                    report_type,
                    date_from,
                    date_to,
                ], spacing=10, wrap=True),
                
                ft.Row([
                    ft.ElevatedButton(
                        "Generate Report",
                        icon=ft.Icons.ANALYTICS,
                        bgcolor="primary",
                        color="onPrimary",
                        on_click=generate_report,
                    ),
                    ft.ElevatedButton(
                        "Export to PDF",
                        icon=ft.Icons.DOWNLOAD,
                        bgcolor="secondary",
                        color="onSecondary",
                        on_click=export_report,
                    ),
                ], spacing=10),
            ], spacing=15),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
        
        ft.Container(height=20),
        
        # Report output area
        ft.Container(
            content=report_output,
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)