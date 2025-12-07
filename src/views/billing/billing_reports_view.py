"""Billing reports showing overall billing situation and analytics - FIXED VERSION."""

import flet as ft
from datetime import datetime, timedelta
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader

def BillingReportsView():
    """Comprehensive billing reports and overall situation analysis."""
    
    user = AppState.get_user()
    
    # Report container with initial message
    report_container = ft.Column(spacing=20)
    
    # Date range filters
    date_from = ft.TextField(
        label="From Date",
        value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        width=150,
        border_color="outline",
    )
    
    date_to = ft.TextField(
        label="To Date",
        value=datetime.now().strftime("%Y-%m-%d"),
        width=150,
        border_color="outline",
    )
    
    def create_metric_card(title, value, icon, color):
        """Helper to create metric cards."""
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=32),
                ft.Text(str(value), size=28, weight="bold", color=color),
                ft.Text(title, size=12, color="outline", text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
            width=200,
        )
    
    def create_revenue_card(title, amount, color):
        """Helper to create revenue cards."""
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=14, color="outline"),
                ft.Text(f"₱{amount:,.2f}", size=24, weight="bold", color=color),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
            width=250,
        )
    
    def generate_report(e):
        """Generate comprehensive billing report."""
        print("🔍 Generate report clicked!")  # Debug
        
        # Clear and show loading
        report_container.controls.clear()
        report_container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.ProgressRing(),
                    ft.Text("Generating report...", size=16),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=50,
            )
        )
        e.page.update()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            date_start = date_from.value
            date_end = date_to.value
            
            print(f"📅 Date range: {date_start} to {date_end}")  # Debug
            
            # 1. Overall Financial Summary
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_invoices,
                    COALESCE(SUM(CASE WHEN status = 'Paid' THEN 1 ELSE 0 END), 0) as paid_count,
                    COALESCE(SUM(CASE WHEN status = 'Unpaid' THEN 1 ELSE 0 END), 0) as unpaid_count,
                    COALESCE(SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END), 0) as cancelled_count,
                    COALESCE(SUM(CASE WHEN status = 'Paid' THEN total_amount ELSE 0 END), 0) as total_revenue,
                    COALESCE(SUM(CASE WHEN status = 'Unpaid' THEN total_amount ELSE 0 END), 0) as pending_revenue,
                    COALESCE(AVG(CASE WHEN status = 'Paid' THEN total_amount END), 0) as avg_invoice_amount
                FROM invoices
                WHERE DATE(created_at) BETWEEN ? AND ?
            """, (date_start, date_end))
            
            summary = cursor.fetchone()
            total_invoices, paid_count, unpaid_count, cancelled_count, total_revenue, pending_revenue, avg_invoice = summary
            
            print(f"📊 Summary: {total_invoices} invoices, ₱{total_revenue} revenue")  # Debug
            
            # 2. Payment Method Breakdown
            cursor.execute("""
                SELECT payment_method, 
                       COUNT(*) as count,
                       SUM(total_amount) as total
                FROM invoices
                WHERE status = 'Paid'
                AND DATE(payment_date) BETWEEN ? AND ?
                GROUP BY payment_method
                ORDER BY total DESC
            """, (date_start, date_end))
            
            payment_methods = cursor.fetchall()
            
            # 3. Top Patients
            cursor.execute("""
                SELECT u.full_name,
                       COUNT(i.id) as invoice_count,
                       SUM(i.total_amount) as total_spent
                FROM invoices i
                LEFT JOIN users u ON i.patient_id = u.id
                WHERE DATE(i.created_at) BETWEEN ? AND ?
                GROUP BY u.full_name
                ORDER BY total_spent DESC
                LIMIT 10
            """, (date_start, date_end))
            
            top_patients = cursor.fetchall()
            
            conn.close()
            
            # Clear loading and build report
            report_container.controls.clear()
            
            # Add report sections
            report_sections = []
            
            # Header
            report_sections.append(
                ft.Text("📊 Overall Billing Situation", size=24, weight="bold")
            )
            
            # Summary container
            report_sections.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"Period: {date_start} to {date_end}", size=14, color="outline"),
                        ft.Divider(height=15),
                        
                        # Metrics Row
                        ft.Row([
                            create_metric_card("Total Invoices", total_invoices, ft.Icons.RECEIPT, "primary"),
                            create_metric_card("Paid", paid_count, ft.Icons.CHECK_CIRCLE, "primary"),
                            create_metric_card("Unpaid", unpaid_count, ft.Icons.PENDING, "error"),
                            create_metric_card("Cancelled", cancelled_count, ft.Icons.CANCEL, "outline"),
                        ], spacing=15, wrap=True, scroll=ft.ScrollMode.AUTO),
                        
                        ft.Container(height=15),
                        
                        # Revenue Row
                        ft.Row([
                            create_revenue_card("Total Revenue", total_revenue, "primary"),
                            create_revenue_card("Pending Revenue", pending_revenue, "error"),
                            create_revenue_card("Average Invoice", avg_invoice, "secondary"),
                        ], spacing=15, wrap=True, scroll=ft.ScrollMode.AUTO),
                    ], spacing=10),
                    padding=20,
                    bgcolor="surface",
                    border_radius=10,
                    border=ft.border.all(1, "outlineVariant"),
                )
            )
            
            # Payment Methods Section
            report_sections.append(ft.Text("💳 Payment Methods Breakdown", size=20, weight="bold"))
            
            payment_method_rows = [
                ft.Row([
                    ft.Text("Method", weight="bold", size=14, expand=True),
                    ft.Text("Transactions", weight="bold", size=14, width=120),
                    ft.Text("Revenue", weight="bold", size=14, width=150),
                ]),
                ft.Divider(),
            ]
            
            if payment_methods:
                for method in payment_methods:
                    payment_method_rows.append(
                        ft.Row([
                            ft.Text(method[0] or "Unknown", size=13, expand=True),
                            ft.Text(str(method[1]), size=13, width=120, color="primary"),
                            ft.Text(f"₱{method[2]:,.2f}", size=13, width=150, color="primary", weight="bold"),
                        ])
                    )
            else:
                payment_method_rows.append(
                    ft.Text("No payment data available", color="outline", italic=True)
                )
            
            report_sections.append(
                ft.Container(
                    content=ft.Column(payment_method_rows, spacing=10),
                    padding=20,
                    bgcolor="surface",
                    border_radius=10,
                    border=ft.border.all(1, "outlineVariant"),
                )
            )
            
            # Top Patients Section
            report_sections.append(ft.Text("👥 Top 10 Patients by Billing", size=20, weight="bold"))
            
            patient_rows = [
                ft.Row([
                    ft.Text("Patient Name", weight="bold", size=14, expand=True),
                    ft.Text("Invoices", weight="bold", size=14, width=100),
                    ft.Text("Total Spent", weight="bold", size=14, width=150),
                ]),
                ft.Divider(),
            ]
            
            if top_patients:
                for patient in top_patients:
                    patient_rows.append(
                        ft.Row([
                            ft.Text(patient[0] or "Unknown", size=13, expand=True),
                            ft.Text(str(patient[1]), size=13, width=100, color="primary"),
                            ft.Text(f"₱{patient[2]:,.2f}", size=13, width=150, color="primary", weight="bold"),
                        ])
                    )
            else:
                patient_rows.append(
                    ft.Text("No patient data available", color="outline", italic=True)
                )
            
            report_sections.append(
                ft.Container(
                    content=ft.Column(patient_rows, spacing=10),
                    padding=20,
                    bgcolor="surface",
                    border_radius=10,
                    border=ft.border.all(1, "outlineVariant"),
                )
            )
            
            # Collection Analysis
            report_sections.append(ft.Text("📊 Collection Analysis", size=20, weight="bold"))
            
            collection_rate = (paid_count / total_invoices * 100) if total_invoices > 0 else 0
            revenue_collection = (total_revenue / (total_revenue + pending_revenue) * 100) if (total_revenue + pending_revenue) > 0 else 0
            
            report_sections.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text("Collection Rate", size=14, color="outline"),
                            ft.Text(f"{collection_rate:.1f}%", size=32, weight="bold", color="primary"),
                            ft.Text("of invoices paid", size=12, color="outline"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                        
                        ft.VerticalDivider(),
                        
                        ft.Column([
                            ft.Text("Revenue Collection", size=14, color="outline"),
                            ft.Text(f"{revenue_collection:.1f}%", size=32, weight="bold", color="primary"),
                            ft.Text("of potential revenue", size=12, color="outline"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                    ]),
                    padding=30,
                    bgcolor="surface",
                    border_radius=10,
                    border=ft.border.all(1, "primary"),
                )
            )
            
            # Add all sections to container
            for section in report_sections:
                report_container.controls.append(section)
            
            print("✅ Report generated successfully!")  # Debug
            e.page.update()
            
        except Exception as ex:
            print(f"❌ Error: {str(ex)}")  # Debug
            report_container.controls.clear()
            report_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, size=60, color="error"),
                        ft.Text("Error generating report", size=18, weight="bold"),
                        ft.Text(str(ex), size=12, color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                )
            )
            conn.close()
            e.page.update()
    
    # Initial state message
    report_container.controls.append(
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ANALYTICS, size=80, color="outline"),
                ft.Text("No report generated yet", size=18, color="outline"),
                ft.Text("Select date range and click 'Generate Report'", size=14, color="outline"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=50,
        )
    )
    
    return ft.Column([
        NavigationHeader(
            "Billing Reports",
            "View overall billing situation and analytics",
            show_back=True,
            back_route="/billing/dashboard"
        ),
        
        ft.Container(
            content=ft.Column([
                # Instructions
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, color="primary"),
                        ft.Text(
                            "View comprehensive billing reports including revenue, payment methods, and top patients.",
                            size=13,
                            expand=True,
                        ),
                    ], spacing=10),
                    padding=15,
                    bgcolor=ft.Colors.with_opacity(0.1, "primary"),
                    border_radius=8,
                ),
                
                ft.Container(height=20),
                
                # Date range selector
                ft.Row([
                    ft.Icon(ft.Icons.DATE_RANGE, color="primary", size=28),
                    ft.Text("Select Report Period", size=20, weight="bold"),
                ], spacing=10),
                
                ft.Row([
                    date_from,
                    ft.Text("to", size=16),
                    date_to,
                    ft.ElevatedButton(
                        "Generate Report",
                        icon=ft.Icons.ANALYTICS,
                        bgcolor="primary",
                        color="white",
                        on_click=generate_report,
                        style=ft.ButtonStyle(
                            padding=15,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                ], spacing=15),
                
                ft.Divider(height=30),
                
                # Report container
                report_container,
            ], spacing=15),
            padding=20,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)