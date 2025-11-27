class AppState:
    current_user = None

    @staticmethod
    def set_user(user_row):
        if user_row:
            # Save just the important info to use later
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