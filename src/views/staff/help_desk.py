"""Help desk / FAQ for staff members."""

import flet as ft
from components.navigation_header import NavigationHeader
from state.app_state import AppState

def HelpDeskView():
    """Staff help desk with FAQs and quick guides."""
    
    user = AppState.get_user()
    
    # Helper to make a question that opens up
    def create_faq(question, answer):
        return ft.ExpansionTile(
            title=ft.Text(question, size=14, weight="bold"),
            subtitle=ft.Text("Click to expand", size=11, color="outline"),
            initially_expanded=False,
            controls=[
                ft.Container(
                    content=ft.Text(answer, size=13),
                    padding=15,
                    bgcolor=ft.Colors.with_opacity(0.05, "primary"),
                    border_radius=8,
                ),
            ],
        )
    
    # Helper to make a step-by-step guide
    def create_guide_card(title, description, icon, steps):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color="primary", size=32),
                    ft.Text(title, size=18, weight="bold"),
                ], spacing=10),
                ft.Text(description, size=13, color="outline"),
                ft.Divider(height=15),
                ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Text(str(idx + 1), size=12, weight="bold", color="white"),
                            width=24,
                            height=24,
                            bgcolor="primary",
                            border_radius=12,
                            alignment=ft.alignment.center,
                        ),
                        ft.Text(step, size=13, expand=True),
                    ], spacing=10)
                    for idx, step in enumerate(steps)
                ], spacing=8),
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    # Helper for the contact info boxes
    def create_contact_card(role, contact_info, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=40),
                ft.Text(role, size=14, weight="bold"),
                ft.Text(contact_info, size=12, color="outline", text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            padding=20,
            border=ft.border.all(1, color),
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.05, color),
            expand=True,
        )
    
    return ft.Column([
        # Header - BACK BUTTON REMOVED
        NavigationHeader(
            "Help Desk",
            "Quick guides and frequently asked questions",
            show_back=False, # Set to False as requested
        ),
        
        ft.Container(
            content=ft.Column([
                # Welcome Banner
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SUPPORT_AGENT, color="primary", size=48),
                        ft.Column([
                            ft.Text("Need Help?", size=24, weight="bold"),
                            ft.Text(
                                "Find answers to common questions and learn how to use the staff portal.",
                                size=14,
                                color="outline",
                            ),
                        ], spacing=5, expand=True),
                    ], spacing=20),
                    padding=20,
                    bgcolor="surface",
                    border_radius=10,
                    border=ft.border.all(1, "outlineVariant"),
                ),
                
                ft.Container(height=30),
                
                # --- GUIDES SECTION ---
                ft.Text("📚 Quick Guides", size=22, weight="bold"),
                
                create_guide_card(
                    "How to Search for a Patient",
                    "Follow these steps to find patient records:",
                    ft.Icons.SEARCH,
                    [
                        "Click 'Find Patients' from the dashboard or sidebar",
                        "Enter the patient's name or phone number in the search field",
                        "Click the 'Search' button or press Enter",
                        "Browse the results and click 'View Full Record' for details",
                    ]
                ),
                
                ft.Container(height=15),
                
                create_guide_card(
                    "Understanding Patient Records",
                    "What information you can access:",
                    ft.Icons.INFO,
                    [
                        "Personal Information: Name, DOB, contact details",
                        "Medical Records: Prescriptions, orders (read-only)",
                        "Registration Date: When the patient joined",
                        "Note: You have VIEW-ONLY access. Contact admin for updates.",
                    ]
                ),
                
                ft.Container(height=15),
                
                create_guide_card(
                    "Assisting Patients",
                    "Best practices when helping patients:",
                    ft.Icons.PEOPLE,
                    [
                        "Always verify patient identity before sharing information",
                        "Be polite and professional in all interactions",
                        "Direct medication questions to pharmacists",
                        "Report any issues or concerns to administrators",
                    ]
                ),
                
                ft.Container(height=30),
                
                # --- FAQ SECTION ---
                ft.Text("❓ Frequently Asked Questions", size=22, weight="bold"),
                
                ft.Container(
                    content=ft.Column([
                        create_faq(
                            "Can I edit patient information?",
                            "No, staff members have read-only access to patient records. If you need to update patient information, please contact the system administrator or ask the patient to update their profile themselves."
                        ),
                        
                        create_faq(
                            "What should I do if a patient's information is incorrect?",
                            "Note down the correct information and submit a request to the administrator. You can also guide the patient to update their profile through the patient portal."
                        ),
                        
                        create_faq(
                            "How do I help a patient who forgot their password?",
                            "Direct the patient to use the 'Forgot Password' link on the login page. If they continue to have issues, contact the administrator to reset their account."
                        ),
                        
                        create_faq(
                            "Can I view prescription details?",
                            "Yes, you can view prescription information for patients, but you cannot approve, reject, or modify prescriptions. Direct prescription-related questions to pharmacists."
                        ),
                        
                        create_faq(
                            "What if the system is running slowly?",
                            "First, try refreshing the page. If the issue persists, report it to the system administrator. Avoid opening multiple tabs of the application."
                        ),
                        
                        create_faq(
                            "How do I report a problem or bug?",
                            "Contact the system administrator immediately with details about the issue, including what you were doing when the problem occurred."
                        ),
                    ], spacing=5),
                    padding=20,
                    border=ft.border.all(1, "outlineVariant"),
                    border_radius=10,
                    bgcolor="surface",
                ),
                
                ft.Container(height=30),
                
                # --- CONTACT SECTION ---
                ft.Text("📞 Need More Help?", size=22, weight="bold"),
                
                ft.Row([
                    create_contact_card(
                        "System Administrator",
                        "admin@pharmacare.com\nExt: 101",
                        ft.Icons.ADMIN_PANEL_SETTINGS,
                        "primary"
                    ),
                    create_contact_card(
                        "Head Pharmacist",
                        "pharmacist@pharmacare.com\nExt: 102",
                        ft.Icons.MEDICAL_SERVICES,
                        "secondary"
                    ),
                    create_contact_card(
                        "IT Support",
                        "support@pharmacare.com\nExt: 103",
                        ft.Icons.SUPPORT,
                        "tertiary"
                    ),
                ], spacing=15),
                
                ft.Container(height=20),
                
                # Footer info
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.INFO, color="outline", size=20),
                            ft.Text("System Information", size=14, weight="bold"),
                        ], spacing=10),
                        ft.Divider(height=10),
                        ft.Text(f"Logged in as: {user['full_name']}", size=12),
                        ft.Text(f"Role: {user['role']}", size=12),
                        ft.Text("Version: 1.0.0", size=12),
                        ft.Text("Last Updated: December 2025", size=12),
                    ], spacing=8),
                    padding=15,
                    border=ft.border.all(1, "outlineVariant"),
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.02, "outline"),
                ),
            ], spacing=0),
            padding=20,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)