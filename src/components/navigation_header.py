"""Simple navigation header with back and forward buttons."""

import flet as ft

def NavigationHeader(title, subtitle="", show_back=True, show_forward=False, back_route=None, forward_route=None):
    """
    Create a navigation header with back/forward buttons.
    
    Usage:
        NavigationHeader("Page Title", "Subtitle", show_back=True)
    """
    
    def go_back(e):
        if back_route:
            e.page.go(back_route)
        else:
            # Go back to dashboard as fallback
            e.page.go("/dashboard")
    
    def go_forward(e):
        if forward_route:
            e.page.go(forward_route)
    
    controls = []
    
    # Back button
    if show_back:
        controls.append(
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color="primary",
                icon_size=28,
                tooltip="Go Back",
                on_click=go_back,
            )
        )
    
    # Title section
    controls.append(
        ft.Column([
            ft.Text(title, size=28, weight="bold"),
            ft.Text(subtitle, size=14, color="outline") if subtitle else ft.Container(),
        ], spacing=5, expand=True)
    )
    
    # Forward button
    if show_forward:
        controls.append(
            ft.IconButton(
                icon=ft.Icons.ARROW_FORWARD,
                icon_color="primary",
                icon_size=28,
                tooltip="Go Forward",
                on_click=go_forward,
            )
        )
    
    return ft.Container(
        content=ft.Row(
            controls, 
            spacing=15, 
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.only(left=10, right=20, top=20, bottom=20),
        bgcolor="surface",
        border=ft.border.only(bottom=ft.BorderSide(1, "outlineVariant")),
    )