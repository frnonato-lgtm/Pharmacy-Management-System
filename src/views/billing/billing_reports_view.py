"""Billing reports showing overall billing situation and analytics - RESTORED FULL VERSION."""

import flet as ft
from datetime import datetime, timedelta
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader

def BillingReportsView():
    """Comprehensive billing reports and overall situation analysis."""
    
    # This container holds all the report sections (Summary, Tables, Analysis)
    report_container = ft.Column(spacing=20)
    
    # Default dates (Last 30 days)
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
    
    # --- UI HELPERS (Small Cards) ---
    def create_metric_card(title, value, icon, color):
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
    
    # --- UI HELPERS (Wide Revenue Cards) ---
    def create_revenue_card(title, amount, color):
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
    
    # --- MAIN REPORT GENERATION LOGIC ---
    def generate_report(e):
        # Clear the previous report so we don't stack them
        report_container.controls.clear()
        
        # Show a loading ring while we fetch data
        report_container.controls.append(ft.ProgressRing())
        e.page.update()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            date_start = date_from.value
            date_end = date_to.value
            
            # 1. GET OVERALL SUMMARY STATS
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
            
            # 2. GET PAYMENT METHODS BREAKDOWN
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
            
            # 3. GET TOP PATIENTS BY SPENDING
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
            
            # --- START BUILDING THE UI ---
            report_container.controls.clear() # Remove loading ring
            
            # SECTION 1: OVERALL SITUATION
            report_container.controls.append(ft.Text("📊 Overall Billing Situation", size=24, weight="bold"))
            
            report_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"Period: {date_start} to {date_end}", size=14, color="outline"),
                        ft.Divider(height=15),
                        
                        # Row of Counts
                        ft.Row([
                            create_metric_card("Total Invoices", total_invoices, ft.Icons.RECEIPT, "primary"),
                            create_metric_card("Paid", paid_count, ft.Icons.CHECK_CIRCLE, "primary"),
                            create_metric_card("Unpaid", unpaid_count, ft.Icons.PENDING, "error"),
                            create_metric_card("Cancelled", cancelled_count, ft.Icons.CANCEL, "outline"),
                        ], spacing=15, wrap=True),
                        
                        ft.Container(height=15),
                        
                        # Row of Money
                        ft.Row([
                            create_revenue_card("Total Revenue", total_revenue, "primary"),
                            create_revenue_card("Pending Revenue", pending_revenue, "error"),
                            create_revenue_card("Average Invoice", avg_invoice, "secondary"),
                        ], spacing=15, wrap=True),
                    ], spacing=10),
                    padding=20,
                    bgcolor="surface",
                    border_radius=10,
                    border=ft.border.all(1, "outlineVariant"),
                )
            )
            
            # SECTION 2: PAYMENT METHODS (The Table)
            report_container.controls.append(ft.Text("💳 Payment Methods Breakdown", size=20, weight="bold"))
            
            payment_rows = [
                ft.Row([
                    ft.Text("Method", weight="bold", expand=True),
                    ft.Text("Transactions", weight="bold", width=120),
                    ft.Text("Revenue", weight="bold", width=150),
                ]),
                ft.Divider(),
            ]
            
            if payment_methods:
                for method in payment_methods:
                    payment_rows.append(
                        ft.Row([
                            ft.Text(method[0] or "Unknown", expand=True),
                            ft.Text(str(method[1]), width=120),
                            ft.Text(f"₱{method[2]:,.2f}", width=150, weight="bold", color="primary"),
                        ])
                    )
            else:
                payment_rows.append(ft.Text("No payment data available for this period.", italic=True))

            report_container.controls.append(
                ft.Container(
                    content=ft.Column(payment_rows, spacing=10),
                    padding=20,
                    bgcolor="surface",
                    border_radius=10,
                    border=ft.border.all(1, "outlineVariant"),
                )
            )
            
            # SECTION 3: TOP PATIENTS (The Table)
            report_container.controls.append(ft.Text("👥 Top 10 Patients by Billing", size=20, weight="bold"))
            
            patient_rows = [
                ft.Row([
                    ft.Text("Patient Name", weight="bold", expand=True),
                    ft.Text("Invoices", weight="bold", width=100),
                    ft.Text("Total Spent", weight="bold", width=150),
                ]),
                ft.Divider(),
            ]
            
            if top_patients:
                for patient in top_patients:
                    patient_rows.append(
                        ft.Row([
                            ft.Text(patient[0] or "Unknown", expand=True),
                            ft.Text(str(patient[1]), width=100),
                            ft.Text(f"₱{patient[2]:,.2f}", width=150, weight="bold", color="primary"),
                        ])
                    )
            else:
                patient_rows.append(ft.Text("No patient data available.", italic=True))
                
            report_container.controls.append(
                ft.Container(
                    content=ft.Column(patient_rows, spacing=10),
                    padding=20,
                    bgcolor="surface",
                    border_radius=10,
                    border=ft.border.all(1, "outlineVariant"),
                )
            )
            
            # SECTION 4: COLLECTION ANALYSIS
            report_container.controls.append(ft.Text("📊 Collection Analysis", size=20, weight="bold"))
            
            # Calculate percentages avoiding division by zero
            collection_rate = (paid_count / total_invoices * 100) if total_invoices > 0 else 0
            revenue_collection = (total_revenue / (total_revenue + pending_revenue) * 100) if (total_revenue + pending_revenue) > 0 else 0
            
            report_container.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text("Invoice Collection Rate", size=14, color="outline"),
                            ft.Text(f"{collection_rate:.1f}%", size=32, weight="bold", color="primary"),
                            ft.Text("of invoices have been paid", size=12, color="outline"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                        
                        ft.VerticalDivider(),
                        
                        ft.Column([
                            ft.Text("Revenue Collection", size=14, color="outline"),
                            ft.Text(f"{revenue_collection:.1f}%", size=32, weight="bold", color="primary"),
                            ft.Text("of total invoiced amount collected", size=12, color="outline"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                    ]),
                    padding=30,
                    bgcolor="surface",
                    border_radius=10,
                    border=ft.border.all(1, "primary"),
                )
            )
            
            e.page.update()
            
        except Exception as ex:
            # Handle errors gracefully
            report_container.controls.clear()
            report_container.controls.append(ft.Text(f"Error generating report: {str(ex)}", color="error"))
            if conn: conn.close()
            e.page.update()
    
    # --- PAGE LAYOUT ---
    return ft.Column([
        # FIXED: Removed the back button (show_back=False)
        NavigationHeader(
            "Billing Reports",
            "View overall billing situation and analytics",
            show_back=False,
        ),
        
        ft.Container(
            content=ft.Column([
                # Filters
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
                    ),
                ], spacing=15),
                
                ft.Divider(height=30),
                
                # The Content Area
                report_container,
            ], spacing=15),
            padding=20,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)