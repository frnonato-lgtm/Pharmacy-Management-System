import flet as ft
from database import authenticate_user, get_db_connection
from state import AppState

def LoginPage(page: ft.Page, role_param="Patient"):
    
    # Define icons for each role
    role_icon_map = {
        "Patient": ft.Icons.PERSON_ADD,
        "Admin": ft.Icons.ADMIN_PANEL_SETTINGS,
        "Pharmacist": ft.Icons.MEDICAL_SERVICES,
        "Inventory": ft.Icons.INVENTORY,
        "Billing": ft.Icons.RECEIPT_LONG,
        "Staff": ft.Icons.BADGE
    }
    
    # Short description under the title
    role_desc_map = {
        "Patient": "Login to access your personal health records",
        "Admin": "Manage system users, configuration, and logs",
        "Pharmacist": "Validate prescriptions and dispense medicines",
        "Inventory": "Track stock levels and manage inventory",
        "Billing": "Process invoices and manage transactions",
        "Staff": "Assist patients and search records"
    }

    current_icon = role_icon_map.get(role_param, ft.Icons.PERSON)
    current_desc = role_desc_map.get(role_param, "Login to your account")
    
    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        e.control.icon = ft.Icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE
        page.update()

    # Standard widths for consistent look
    INPUT_WIDTH_LOGIN = 320
    INPUT_WIDTH_SIGNUP = 450 

    # Helper to make all textboxes look the same
    def create_field(label, icon=None, password=False, width=None):
        return ft.TextField(
            label=label,
            prefix_icon=icon,
            width=width,
            height=45,
            text_size=13,
            border_color="outline",
            bgcolor="surface",
            password=password,
            can_reveal_password=password,
            content_padding=10,
            focused_border_color="primary"
        )

    # --- LOGIN INPUTS ---
    login_user = create_field("Username", ft.Icons.PERSON, width=INPUT_WIDTH_LOGIN)
    login_pass = create_field("Password", ft.Icons.LOCK, password=True, width=INPUT_WIDTH_LOGIN)
    login_error = ft.Text(color="error", size=12, text_align="center")

    def handle_login(e):
        user = authenticate_user(login_user.value, login_pass.value)
        if user:
            # Prevent logging in as wrong role
            if user['role'] != role_param and user['role'] != 'Admin':
                login_error.value = f"Access Denied. You are not a {role_param}."
                page.update()
                return
            AppState.set_user(user)
            page.go("/dashboard")
        else:
            login_error.value = "Invalid Username or Password"
            page.update()

    # --- SIGNUP INPUTS ---
    su_first = create_field("First Name", width=INPUT_WIDTH_SIGNUP)
    su_last = create_field("Last Name", width=INPUT_WIDTH_SIGNUP)
    su_email = create_field("Email Address", ft.Icons.EMAIL_OUTLINED, width=INPUT_WIDTH_SIGNUP)
    su_phone = create_field("Phone Number", ft.Icons.PHONE_OUTLINED, width=INPUT_WIDTH_SIGNUP)
    su_dob = create_field("Date of Birth (YYYY-MM-DD)", ft.Icons.CALENDAR_TODAY, width=INPUT_WIDTH_SIGNUP)
    su_addr = create_field("Address", ft.Icons.HOME_OUTLINED, width=INPUT_WIDTH_SIGNUP)
    su_user = create_field("Username", ft.Icons.ACCOUNT_CIRCLE, width=INPUT_WIDTH_SIGNUP)
    su_pass = create_field("Password", ft.Icons.LOCK_OUTLINE, password=True, width=INPUT_WIDTH_SIGNUP)
    su_confirm = create_field("Confirm Password", ft.Icons.LOCK_OUTLINE, password=True, width=INPUT_WIDTH_SIGNUP)
    su_terms = ft.Checkbox(label="I agree to Terms and Conditions", value=False, label_style=ft.TextStyle(size=12))
    su_error = ft.Text(color="error", size=12, text_align="center")
    su_success = ft.Text(color="primary", size=12, text_align="center")

    def handle_signup(e):
        # Basic checks
        if not all([su_first.value, su_last.value, su_email.value, su_phone.value, su_user.value, su_pass.value]):
            su_error.value = "Please fill in all required fields."
            page.update()
            return
        if su_pass.value != su_confirm.value:
            su_error.value = "Passwords do not match."
            page.update()
            return
        if not su_terms.value:
            su_error.value = "You must agree to the Terms."
            page.update()
            return

        # Save to DB
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO users (username, password, role, full_name, last_name, email, phone, dob, address) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (su_user.value, su_pass.value, 'Patient', su_first.value, su_last.value, su_email.value, su_phone.value, su_dob.value, su_addr.value)
            )
            conn.commit()
            conn.close()
            su_success.value = "Account created! Please Login."
            su_error.value = ""
        except:
            su_error.value = "Username already exists."
        page.update()

    # --- TOP LEFT BUTTON ---
    back_btn = ft.TextButton(
        "Back to Home", 
        icon=ft.Icons.ARROW_BACK, 
        icon_color="primary",
        on_click=lambda _: page.go("/")
    )

    # Container that animates size
    main_card_container = ft.Container(
        padding=35,
        width=420, # Standard width for login
        animate=ft.Animation(300, "easeOut") 
    )

    def switch_to_signup(e):
        back_btn.text = "Back to Login"
        back_btn.on_click = lambda _: switch_to_login(None)
        main_card_container.width = 550 # Make it wider for sign up form
        render_signup()

    def switch_to_login(e):
        back_btn.text = "Back to Home"
        back_btn.on_click = lambda _: page.go("/")
        main_card_container.width = 420 # Back to narrow for login
        render_login()

    # --- RENDER FUNCTIONS ---
    form_container = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)

    def render_login():
        demo_text = ""
        if role_param == "Admin": demo_text = "admin / admin123"
        elif role_param == "Pharmacist": demo_text = "pharm / pharm123"
        elif role_param == "Inventory": demo_text = "inv / inv123"
        elif role_param == "Billing": demo_text = "bill / bill123"
        elif role_param == "Staff": demo_text = "staff / staff123"

        demo_box = ft.Container()
        if role_param != "Patient":
            demo_box = ft.Container(
                bgcolor="secondaryContainer", padding=10, border_radius=5,
                content=ft.Text(f"Demo: {demo_text}", size=11, color="onSecondaryContainer")
            )

        form_container.controls = [
            ft.Icon(current_icon, size=50, color="primary"),
            ft.Text(f"{role_param} Login", size=22, weight="bold", color="onSurface"),
            ft.Text(current_desc, size=12, color="outline", text_align="center"),
            
            ft.Container(height=15),
            ft.Divider(height=1, thickness=1, color="outlineVariant"),
            ft.Container(height=20),
            
            login_user,
            ft.Container(height=10),
            login_pass,
            
            ft.Container(height=25), # Increased space
            ft.ElevatedButton("Login", width=INPUT_WIDTH_LOGIN, height=45, on_click=handle_login, bgcolor="primary", color="onPrimary", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
            
            ft.Container(height=10),
            login_error,
            
            ft.Container(height=10), 
            ft.Divider(height=1, thickness=1, color="outlineVariant") if role_param != "Patient" else ft.Container(),
            ft.Container(height=15),
            
            demo_box,
        ]
        if role_param == "Patient":
            form_container.controls.append(ft.Divider(height=1, thickness=1, color="outlineVariant"))
            form_container.controls.append(ft.Container(height=15))
            form_container.controls.append(ft.TextButton("Create Account", on_click=switch_to_signup))
        
        main_card_container.content = form_container
        page.update()

    def render_signup():
        form_container.controls = [
            ft.Icon(ft.Icons.PERSON_ADD, size=40, color="primary"),
            ft.Text("Create Patient Account", size=20, weight="bold", color="onSurface"),
            ft.Text("Register to browse medicines and manage orders", size=12, color="outline"),
            
            ft.Container(height=15),
            ft.Divider(height=1, thickness=1, color="outlineVariant"),
            ft.Container(height=15),
            
            ft.Text("Personal Information", size=13, weight="bold", color="onSurfaceVariant"),
            ft.Container(height=10),
            
            su_first, 
            ft.Container(height=8), 
            su_last,
            
            ft.Container(height=8),
            su_email,
            ft.Container(height=8),
            su_phone,
            
            ft.Container(height=20),
            ft.Divider(height=1, thickness=1, color="outlineVariant"),
            ft.Container(height=15),
            
            ft.Text("Additional Information", size=13, weight="bold", color="onSurfaceVariant"),
            ft.Container(height=10),
            su_dob,
            ft.Container(height=8),
            su_addr,
            
            ft.Container(height=20),
            ft.Divider(height=1, thickness=1, color="outlineVariant"),
            ft.Container(height=15),
            
            ft.Text("Account Credentials", size=13, weight="bold", color="onSurfaceVariant"),
            ft.Container(height=10),
            su_user,
            ft.Container(height=8),
            su_pass,
            ft.Container(height=8),
            su_confirm,
            
            ft.Container(height=10),
            ft.Row([su_terms], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Container(height=15),
            ft.ElevatedButton("Create Account", width=250, height=45, on_click=handle_signup, bgcolor="primary", color="onPrimary", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
            
            su_error,
            su_success,
            
            ft.Container(height=25), # Bottom space
        ]
        main_card_container.content = form_container
        page.update()

    render_login()

    # Main Page Layout
    return ft.Column(
        expand=True,
        controls=[
            # Top bar area
            ft.Container(
                padding=ft.padding.symmetric(horizontal=20, vertical=15),
                content=ft.Row([
                    back_btn, 
                    ft.IconButton(ft.Icons.DARK_MODE, on_click=toggle_theme, tooltip="Toggle Theme")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ),

            # Center Card
            ft.Container(
                expand=True,
                alignment=ft.alignment.center, 
                padding=ft.padding.only(bottom=50),
                content=ft.Card(
                    elevation=5,
                    surface_tint_color="surface",
                    color="surface",
                    shape=ft.RoundedRectangleBorder(radius=12),
                    content=main_card_container 
                ),
            )
        ]
    )