"""Create invoice view with automatic calculations."""

import flet as ft
from datetime import datetime
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader
import random

def CreateInvoicesView():
    """Create new invoice with automatic calculations and billing."""
    
    user = AppState.get_user()
    
    # --- FETCH DATA ---
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, full_name, email FROM users WHERE role = 'Patient'")
    patients = cursor.fetchall()
    
    cursor.execute("""
        SELECT o.id, o.patient_id, u.full_name, o.total_amount, o.order_date
        FROM orders o
        LEFT JOIN users u ON o.patient_id = u.id
        WHERE o.payment_status = 'Unpaid'
        ORDER BY o.order_date DESC
    """)
    orders = cursor.fetchall()
    
    conn.close()
    
    # --- FORM FIELDS ---
    patient_dropdown = ft.Dropdown(
        label="Select Patient *",
        options=[ft.dropdown.Option(key=str(p[0]), text=f"{p[1]} ({p[2]})") for p in patients],
        width=300,
        border_color="outline",
    )
    
    order_dropdown = ft.Dropdown(
        label="Select Order (Optional)",
        options=[ft.dropdown.Option("None")] + [
            ft.dropdown.Option(key=str(o[0]), text=f"Order #{o[0]} - ₱{o[3]:,.2f} ({o[4]})") 
            for o in orders
        ],
        value="None",
        width=400,
        border_color="outline",
    )
    
    subtotal_field = ft.TextField(label="Subtotal *", value="0.00", prefix_text="₱", keyboard_type=ft.KeyboardType.NUMBER, width=200, border_color="outline")
    tax_field = ft.TextField(label="Tax (12%)", value="0.00", prefix_text="₱", keyboard_type=ft.KeyboardType.NUMBER, width=200, read_only=True, border_color="outline")
    discount_field = ft.TextField(label="Discount", value="0.00", prefix_text="₱", keyboard_type=ft.KeyboardType.NUMBER, width=200, border_color="outline")
    total_field = ft.TextField(label="Total Amount", value="0.00", prefix_text="₱", read_only=True, width=200, border_color="outline")
    
    payment_method = ft.Dropdown(
        label="Payment Method",
        options=[ft.dropdown.Option("Cash"), ft.dropdown.Option("Credit Card"), ft.dropdown.Option("Debit Card"), ft.dropdown.Option("Bank Transfer"), ft.dropdown.Option("GCash"), ft.dropdown.Option("PayMaya")],
        value="Cash",
        width=200,
        border_color="outline",
    )
    
    notes_field = ft.TextField(label="Notes (Optional)", multiline=True, min_lines=3, max_lines=5, width=700, border_color="outline") # INCREASED WIDTH
    
    # --- CALCULATIONS ---
    def calculate_total(e):
        try:
            subtotal = float(subtotal_field.value or 0)
            discount = float(discount_field.value or 0)
            tax = subtotal * 0.12
            tax_field.value = f"{tax:.2f}"
            total = subtotal + tax - discount
            total_field.value = f"{total:.2f}"
            e.page.update()
        except: pass
    
    subtotal_field.on_change = calculate_total
    discount_field.on_change = calculate_total
    
    def on_order_selected(e):
        if order_dropdown.value != "None":
            order_id = int(order_dropdown.value)
            selected_order = next((o for o in orders if o[0] == order_id), None)
            if selected_order:
                subtotal_field.value = f"{selected_order[3]:.2f}"
                patient_dropdown.value = str(selected_order[1])
                calculate_total(e)
    
    order_dropdown.on_change = on_order_selected
    
    # --- CREATE LOGIC ---
    def create_invoice(e):
        if not patient_dropdown.value:
            e.page.snack_bar = ft.SnackBar(content=ft.Text("Please select a patient"), bgcolor="error")
            e.page.snack_bar.open = True
            e.page.update()
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            patient_id = int(patient_dropdown.value)
            order_id = int(order_dropdown.value) if order_dropdown.value != "None" else None
            subtotal = float(subtotal_field.value)
            tax = float(tax_field.value)
            discount = float(discount_field.value)
            total = float(total_field.value)
            
            cursor.execute("""
                INSERT INTO invoices 
                (invoice_number, patient_id, order_id, subtotal, tax, discount, total_amount, 
                 status, payment_method, billing_clerk_id, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Unpaid', ?, ?, ?, ?)
            """, (invoice_number, patient_id, order_id, subtotal, tax, discount, total, payment_method.value, user['id'], notes_field.value or "", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            invoice_id = cursor.lastrowid
            
            cursor.execute("""
                INSERT INTO activity_log (user_id, action, details, timestamp)
                VALUES (?, 'invoice_created', ?, ?)
            """, (user['id'], f"Created invoice {invoice_number} for patient ID {patient_id} - Amount: ₱{total:,.2f}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            if order_id:
                cursor.execute("UPDATE orders SET payment_status = 'Invoiced' WHERE id = ?", (order_id,))
            
            conn.commit()
            conn.close()
            
            e.page.snack_bar = ft.SnackBar(content=ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE, color="white"), ft.Text(f"Invoice {invoice_number} created successfully!", color="white")]), bgcolor="primary")
            e.page.snack_bar.open = True
            
            e.page.go(f"/billing/invoice/{invoice_id}")
            
        except Exception as ex:
            conn.rollback()
            conn.close()
            e.page.snack_bar = ft.SnackBar(content=ft.Text(f"Error creating invoice: {str(ex)}"), bgcolor="error")
            e.page.snack_bar.open = True
            e.page.update()
    
    # --- PAGE LAYOUT ---
    # I set this container width to 800 to make it wider and more professional
    return ft.Column([
        NavigationHeader(
            "Create Invoice",
            "Generate invoice for patient billing",
            show_back=True,
            back_route="/billing/invoices"
        ),
        
        ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([ft.Icon(ft.Icons.INFO_OUTLINE, color="primary"), ft.Text("Create a new invoice for a patient. You can link it to an existing order or enter manual amounts.", size=13, expand=True)], spacing=10),
                    padding=15, bgcolor=ft.Colors.with_opacity(0.1, "primary"), border_radius=8
                ),
                
                ft.Container(height=20),
                
                ft.Text("Patient Information", size=20, weight="bold"),
                ft.Row([patient_dropdown, order_dropdown], spacing=15),
                
                ft.Container(height=20),
                
                ft.Text("Amount Details", size=20, weight="bold"),
                ft.Row([subtotal_field, tax_field, discount_field, total_field], spacing=15, wrap=True),
                
                ft.Container(height=20),
                
                ft.Text("Payment Information", size=20, weight="bold"),
                payment_method,
                
                ft.Container(height=20),
                
                ft.Text("Additional Notes", size=20, weight="bold"),
                notes_field,
                
                ft.Container(height=30),
                
                ft.Row([
                    ft.ElevatedButton(
                        content=ft.Row([ft.Icon(ft.Icons.SAVE, color="white"), ft.Text("Create Invoice", color="white")], spacing=10),
                        bgcolor="primary",
                        style=ft.ButtonStyle(padding=15, shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=create_invoice,
                    ),
                    ft.OutlinedButton(
                        "Cancel",
                        icon=ft.Icons.CANCEL,
                        on_click=lambda e: e.page.go("/billing/invoices"),
                        style=ft.ButtonStyle(padding=15, shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                ], spacing=10),
            ], spacing=0),
            padding=40, # Added more padding for a cleaner look
            width=900, # WIDER LAYOUT (Requested fix)
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)