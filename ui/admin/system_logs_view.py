"""System activity logs and audit trail."""

import flet as ft
from database import get_db_connection
from datetime import datetime, timedelta

def SystemLogs():
    """System logs and activity monitoring."""
    
    logs_container = ft.Column(spacing=10)
    
    # Filter controls
    log_type_filter = ft.Dropdown(
        label="Log Type",
        options=[
            ft.dropdown.Option("all", "All Activities"),
            ft.dropdown.Option("login", "User Logins"),
            ft.dropdown.Option("user_management", "User Management"),
            ft.dropdown.Option("inventory", "Inventory Changes"),
            ft.dropdown.Option("prescriptions", "Prescription Actions"),
            ft.dropdown.Option("system", "System Events"),
        ],
        value="all",
        width=250,
    )
    
    date_filter = ft.Dropdown(
        label="Time Period",
        options=[
            ft.dropdown.Option("today", "Today"),
            ft.dropdown.Option("week", "Last 7 Days"),
            ft.dropdown.Option("month", "Last 30 Days"),
            ft.dropdown.Option("all", "All Time"),
        ],
        value="week",
        width=200,
    )
    
    search_field = ft.TextField(
        hint_text="Search logs...",
        prefix_icon=ft.Icons.SEARCH,
        border_color="outline",
        width=300,
    )
    
    def get_mock_logs():
        """Generate mock activity logs (replace with real database logs)."""
        now = datetime.now()
        #for now activity timeline a mock page to see how sysact_log work
        mock_logs = [
            {
                "id": 1,
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "user": "admin",
                "action": "Logged in",
                "details": "Admin user logged into the system",
                "type": "login",
                "icon": ft.Icons.LOGIN,
                "color": "primary",
            },
            {
                "id": 2,
                "timestamp": (now - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
                "user": "Dr. Sarah Chen",
                "action": "Approved Prescription",
                "details": "Approved prescription #1234 for John Doe",
                "type": "prescriptions",
                "icon": ft.Icons.CHECK_CIRCLE,
                "color": "primary",
            },
            {
                "id": 3,
                "timestamp": (now - timedelta(minutes=32)).strftime("%Y-%m-%d %H:%M:%S"),
                "user": "admin",
                "action": "User Deleted",
                "details": "Deleted user 'test_user' from the system",
                "type": "user_management",
                "icon": ft.Icons.DELETE,
                "color": "error",
            },
            {
                "id": 4,
                "timestamp": (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "user": "Mike Johnson",
                "action": "Inventory Update",
                "details": "Updated stock for Paracetamol 500mg: +100 units",
                "type": "inventory",
                "icon": ft.Icons.INVENTORY,
                "color": "secondary",
            },
            {
                "id": 5,
                "timestamp": (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
                "user": "John Doe",
                "action": "Account Created",
                "details": "New patient registered in the system",
                "type": "user_management",
                "icon": ft.Icons.PERSON_ADD,
                "color": "primary",
            },
            {
                "id": 6,
                "timestamp": (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
                "user": "Lisa Martinez",
                "action": "Invoice Generated",
                "details": "Generated invoice #5001 for ₱450.00",
                "type": "billing",
                "icon": ft.Icons.RECEIPT,
                "color": "tertiary",
            },
            {
                "id": 7,
                "timestamp": (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
                "user": "system",
                "action": "Low Stock Alert",
                "details": "Vitamin C stock dropped below reorder level (5 units)",
                "type": "system",
                "icon": ft.Icons.WARNING,
                "color": "error",
            },
            {
                "id": 8,
                "timestamp": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "user": "admin",
                "action": "System Backup",
                "details": "Automated database backup completed successfully",
                "type": "system",
                "icon": ft.Icons.BACKUP,
                "color": "primary",
            },
            {
                "id": 9,
                "timestamp": (now - timedelta(days=1, hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
                "user": "Dr. Sarah Chen",
                "action": "Rejected Prescription",
                "details": "Rejected prescription #1230 - Invalid doctor signature",
                "type": "prescriptions",
                "icon": ft.Icons.CANCEL,
                "color": "error",
            },
            {
                "id": 10,
                "timestamp": (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
                "user": "Anna Garcia",
                "action": "Patient Record Accessed",
                "details": "Viewed patient record for Jane Smith #4567",
                "type": "user_management",
                "icon": ft.Icons.VISIBILITY,
                "color": "outline",
            },
        ]
        
        # In real implementation, query from database: so for now since the db for other views are not implemented
        #we use mock_logs or a fake stats
        # conn = get_db_connection()
        # cursor = conn.cursor()
        # cursor.execute("SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT 50")
        # logs = cursor.fetchall()
        # conn.close()
        #example if real implementation:
        # Get recent medicines (pharmacist) for inventory logs
        #cursor.execute("SELECT name, category, stock FROM medicines ORDER BY id DESC LIMIT 5")
        #recent_medicines = cursor.fetchall()



        return mock_logs
    
    def create_log_entry(log):
        """Create a log entry card."""
        # Format time nicely
        try:
            log_time = datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S")
            time_ago = get_time_ago(log_time)
        except:
            time_ago = log['timestamp']
        
        return ft.Container(
            content=ft.Row([
                # Icon
                ft.Container(
                    content=ft.Icon(log['icon'], color=log['color'], size=24),
                    bgcolor=ft.Colors.with_opacity(0.1, log['color']),
                    width=50,
                    height=50,
                    border_radius=25,
                    alignment=ft.alignment.center,
                ),
                # Log details
                ft.Column([
                    ft.Row([
                        ft.Text(log['action'], size=15, weight="bold"),
                        ft.Container(
                            content=ft.Text(log['type'], size=11, color="onSecondaryContainer"),
                            bgcolor="secondaryContainer",
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            border_radius=10,
                        ),
                    ], spacing=10),
                    ft.Text(log['details'], size=13, color="outline"),
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON, size=14, color="outline"),
                        ft.Text(log['user'], size=12, color="outline"),
                        ft.Icon(ft.Icons.ACCESS_TIME, size=14, color="outline"),
                        ft.Text(time_ago, size=12, color="outline"),
                    ], spacing=5),
                ], spacing=5, expand=True),
                # More options
                ft.IconButton(
                    icon=ft.Icons.MORE_VERT,
                    icon_color="outline",
                    tooltip="More options",
                ),
            ], spacing=15),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    def get_time_ago(log_time):
        """Convert datetime to 'time ago' format."""
        now = datetime.now()
        diff = now - log_time
        
        if diff.days > 30:
            return f"{diff.days // 30} months ago"
        elif diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return "Just now"
    
    def load_logs(e=None):
        """Load and filter logs."""
        logs_container.controls.clear()
        
        # Get logs (mock for now)
        all_logs = get_mock_logs()
        
        # Apply filters
        log_type = log_type_filter.value
        date_range = date_filter.value
        search_query = search_field.value.lower() if search_field.value else ""
        
        # Filter by type
        if log_type != "all":
            all_logs = [log for log in all_logs if log['type'] == log_type]
        
        # Filter by date
        if date_range != "all":
            now = datetime.now()
            if date_range == "today":
                cutoff = now.replace(hour=0, minute=0, second=0)
            elif date_range == "week":
                cutoff = now - timedelta(days=7)
            else:  # month
                cutoff = now - timedelta(days=30)
            
            all_logs = [
                log for log in all_logs 
                if datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S") >= cutoff
            ]
        
        # Filter by search
        if search_query:
            all_logs = [
                log for log in all_logs
                if search_query in log['action'].lower() 
                or search_query in log['details'].lower()
                or search_query in log['user'].lower()
            ]
        
        # Display logs
        if all_logs:
            logs_container.controls.append(
                ft.Text(
                    f"Showing {len(all_logs)} log entries",
                    size=14,
                    color="outline",
                    weight="bold",
                )
            )
            
            for log in all_logs:
                logs_container.controls.append(create_log_entry(log))
        else:
            logs_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF, size=80, color="outline"),
                        ft.Text("No logs found", size=18, color="outline"),
                        ft.Text("Try adjusting your filters", size=14, color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.alignment.center,
                )
            )
        
        if e:
            e.page.update()
    
    def export_logs(e):
        """Export logs to file."""
        e.page.snack_bar = ft.SnackBar(
            content=ft.Text("Export feature coming soon!"),
            bgcolor="secondary",
        )
        e.page.snack_bar.open = True
        e.page.update()
    
    def clear_logs(e):
        """Clear old logs (with confirmation)."""
        def confirm_clear(dialog_e):
            dialog.open = False
            e.page.snack_bar = ft.SnackBar(
                content=ft.Text("Old logs cleared successfully!"),
                bgcolor="primary",
            )
            e.page.snack_bar.open = True
            e.page.update()
            load_logs(e)
        
        def cancel_clear(dialog_e):
            dialog.open = False
            e.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Clear Logs"),
            content=ft.Text("Are you sure you want to clear logs older than 30 days? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_clear),
                ft.ElevatedButton("Clear Logs", bgcolor="error", color="onError", on_click=confirm_clear),
            ],
        )
        e.page.dialog = dialog
        dialog.open = True
        e.page.update()
    
    # Initial load
    class FakePage:
        dialog = None
        snack_bar = None
        def update(self): pass
    load_logs(type('Event', (), {'page': FakePage()})())
    
    return ft.Column([
        # Header
        ft.Row([
            ft.Text("System Activity Logs", size=28, weight="bold"),
        ]),
        ft.Text("Monitor user activities and system events", size=14, color="outline"),
        
        ft.Container(height=20),
        
        # Filters and controls
        ft.Container(
            content=ft.Column([
                ft.Row([
                    log_type_filter,
                    date_filter,
                    search_field,
                ], spacing=10, wrap=True),
                
                ft.Row([
                    ft.ElevatedButton(
                        "Refresh Logs",
                        icon=ft.Icons.REFRESH,
                        bgcolor="primary",
                        color="onPrimary",
                        on_click=load_logs,
                    ),
                    ft.ElevatedButton(
                        "Export Logs",
                        icon=ft.Icons.DOWNLOAD,
                        bgcolor="secondary",
                        color="onSecondary",
                        on_click=export_logs,
                    ),
                    ft.OutlinedButton(
                        "Clear Old Logs",
                        icon=ft.Icons.DELETE_SWEEP,
                        on_click=clear_logs,
                    ),
                ], spacing=10, wrap=True),
            ], spacing=15),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
        
        ft.Container(height=20),
        
        # Activity timeline
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.TIMELINE, color="primary", size=24),
                    ft.Text("Activity Timeline", size=20, weight="bold"),
                ], spacing=10),
                ft.Divider(height=20),
                logs_container,
            ], spacing=10),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)