# A simple class to remember who is currently logged in
class AppState:
    current_user = None
    app_layout = None  # Reference to AppLayout for global success indicator
    _listeners = {}

    @staticmethod
    def set_user(user_row):
        if user_row:
            # Save the important details
            AppState.current_user = {
                "id": user_row["id"],
                "username": user_row["username"],
                "role": user_row["role"],
                "full_name": user_row["full_name"]
            }
        else:
            AppState.current_user = None

    @staticmethod
    def get_user():
        return AppState.current_user
    
    @staticmethod
    def set_app_layout(layout):
        """Store the AppLayout reference for global access"""
        AppState.app_layout = layout
    
    @staticmethod
    def show_success(duration=2):
        """Show the success indicator from anywhere in the app"""
        if AppState.app_layout:
            AppState.app_layout.show_success_indicator(duration)
    
    @staticmethod
    def add_listener(event_name, callback):
        """Register a listener for an event."""
        if event_name not in AppState._listeners:
            AppState._listeners[event_name] = []
        AppState._listeners[event_name].append(callback)
    
    @staticmethod
    def remove_listener(event_name, callback):
        """Remove a listener for an event."""
        if event_name in AppState._listeners:
            if callback in AppState._listeners[event_name]:
                AppState._listeners[event_name].remove(callback)
    
    @staticmethod
    def emit(event_name, *args, **kwargs):
        """Emit an event to all registered listeners."""
        if event_name in AppState._listeners:
            for callback in AppState._listeners[event_name]:
                try:
                    callback(*args, **kwargs)
                except Exception:
                    pass