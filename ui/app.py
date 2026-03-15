import customtkinter as ctk
from PIL import Image
import os
from core.paths import get_resource_path
from ui.views.home import HomeView
from ui.views.settings import SettingsView
from ui.views.downloads import DownloadsView
from core.launcher import init_discord_rpc

class LauncherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Minecraft Launcher")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.bg_image_path = get_resource_path(os.path.join("ui", "assets", "bg.png"))
        if os.path.exists(self.bg_image_path):
            img = Image.open(self.bg_image_path)
            self.bg_ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(900, 600))
            self.bg_label = ctk.CTkLabel(self, image=self.bg_ctk_image, text="")
            self.bg_label.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
            self.bind("<Configure>", self._resize_bg)

        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#181818")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="MC Launcher", 
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color="#00A859"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))

        icon_size = (20, 20)
        self.home_icon = ctk.CTkImage(Image.open(get_resource_path(os.path.join("ui", "assets", "icons", "home.png"))), size=icon_size)
        self.settings_icon = ctk.CTkImage(Image.open(get_resource_path(os.path.join("ui", "assets", "icons", "settings.png"))), size=icon_size)
        self.downloads_icon = ctk.CTkImage(Image.open(get_resource_path(os.path.join("ui", "assets", "icons", "downloads.png"))), size=icon_size)

        self.home_button = ctk.CTkButton(
            self.sidebar_frame, 
            corner_radius=0, 
            height=50, 
            border_spacing=10, 
            text=" Home",
            image=self.home_icon,
            fg_color="transparent", 
            text_color=("gray10", "gray90"), 
            hover_color=("gray70", "gray30"),
            anchor="w", 
            command=self.show_home_view
        )
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.settings_button = ctk.CTkButton(
            self.sidebar_frame, 
            corner_radius=0, 
            height=50, 
            border_spacing=10, 
            text=" Settings",
            image=self.settings_icon,
            fg_color="transparent", 
            text_color=("gray10", "gray90"), 
            hover_color=("gray70", "gray30"),
            anchor="w", 
            command=self.show_settings_view
        )
        self.settings_button.grid(row=2, column=0, sticky="ew")

        self.downloads_button = ctk.CTkButton(
            self.sidebar_frame, 
            corner_radius=0, 
            height=50, 
            border_spacing=10, 
            text=" Downloads",
            image=self.downloads_icon,
            fg_color="transparent", 
            text_color=("gray10", "gray90"), 
            hover_color=("gray70", "gray30"),
            anchor="w", 
            command=self.show_downloads_view
        )
        self.downloads_button.grid(row=3, column=0, sticky="ew")

        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.home_view = HomeView(self.main_container)
        self.settings_view = SettingsView(self.main_container)
        self.downloads_view = DownloadsView(self.main_container, on_download_complete=self.home_view.fetch_versions)

        self.current_view = None
        self.show_home_view()

        init_discord_rpc()

    def select_sidebar_button(self, name):
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.settings_button.configure(fg_color=("gray75", "gray25") if name == "settings" else "transparent")
        self.downloads_button.configure(fg_color=("gray75", "gray25") if name == "downloads" else "transparent")

    def _resize_bg(self, event):
        if event.widget == self and hasattr(self, 'bg_ctk_image'):
            w, h = self.winfo_width(), self.winfo_height()
            if w > 10 and h > 10:
                self.bg_ctk_image.configure(size=(w, h))

    def show_view(self, view, name):
        if self.current_view == view:
            return
            
        prev_view = self.current_view
        self.current_view = view
        
        view.place(relx=1.0, rely=0, relwidth=1.0, relheight=1.0)
        view.lift() # Bring to front
        
        self._animate_slide(view, prev_view)
        self.select_sidebar_button(name)
        
        if name == "home" and hasattr(self.settings_view, 'inputs'):
            self.home_view.username_input.set(self.settings_view.inputs["username"].get())
        elif name == "settings" and hasattr(self.home_view, 'username_input'):
            self.settings_view.inputs["username"].set(self.home_view.username_input.get())

    def _animate_slide(self, view, prev_view, step=0.0):
        if step >= 1.0:
            view.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
            if prev_view:
                prev_view.place_forget()
            return

        x = (1.0 - step) ** 3
        view.place(relx=x, rely=0, relwidth=1.0, relheight=1.0)
        
        self.after(5, lambda: self._animate_slide(view, prev_view, step + 0.02))

    def show_home_view(self):
        self.show_view(self.home_view, "home")

    def show_settings_view(self):
        self.show_view(self.settings_view, "settings")

    def show_downloads_view(self):
        self.show_view(self.downloads_view, "downloads")
