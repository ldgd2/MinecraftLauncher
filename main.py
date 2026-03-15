import customtkinter as ctk
from ui.app import LauncherApp

def main():
    # Set default color theme and appearance
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("green")

    # Initialize main application
    app = LauncherApp()
    
    # Run the event loop
    app.mainloop()

if __name__ == "__main__":
    main()
