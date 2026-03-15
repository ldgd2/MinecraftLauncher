import customtkinter as ctk
from config.manager import config
from PIL import Image
from core.paths import get_resource_path
import threading
import time
import os
import subprocess
from core.versions import get_installed_versions
from core.launcher import launch_minecraft, update_discord_rpc
from ui.components.buttons import PremiumButton
from ui.components.inputs import StyledInputRow

class HomeView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.08)
        
        self.header = ctk.CTkLabel(self.header_frame, text="Welcome Back", font=ctk.CTkFont(family="Inter", size=36, weight="bold"))
        self.header.grid(row=0, column=0, sticky="w")
        
        icon_path = get_resource_path(os.path.join("ui", "assets", "icons", "folder.png"))
        self.folder_icon = ctk.CTkImage(Image.open(icon_path), size=(20, 20)) if os.path.exists(icon_path) else None

        self.mods_button = PremiumButton(
            self.header_frame, 
            text=" Mods Folder", 
            image=self.folder_icon,
            command=self.open_mods_folder,
            variant="secondary",
            height=35
        )
        self.mods_button.grid(row=0, column=1, padx=20, sticky="e")
        self.header_frame.grid_columnconfigure(1, weight=1)

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.place(relx=0.05, rely=0.15, relwidth=0.9, relheight=0.65)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.username_input = StyledInputRow(
            self.main_container,
            "Username",
            "Change your in-game nickname",
            config.get("username"),
            "string",
            self.update_username
        )
        self.username_input.grid(row=0, column=0, pady=15, sticky="ew")

        self.version_select_frame = ctk.CTkFrame(self.main_container, fg_color="#181818", corner_radius=15, border_width=1, border_color="#333333")
        self.version_select_frame.grid(row=1, column=0, pady=15, sticky="ew")
        self.version_select_frame.grid_columnconfigure(1, weight=1)

        self.version_label = ctk.CTkLabel(self.version_select_frame, text="Version:", font=ctk.CTkFont(size=14, weight="bold"))
        self.version_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.version_var = ctk.StringVar(value="Loading...")
        self.version_menu = ctk.CTkOptionMenu(
            self.version_select_frame, 
            variable=self.version_var, 
            values=["Loading..."],
            fg_color="#111111",
            button_color="#222222",
            button_hover_color="#333333",
            corner_radius=10,
            command=self.on_version_change
        )
        self.version_menu.grid(row=0, column=1, padx=20, pady=20, sticky="ew")

        self.stats_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.stats_frame.grid(row=2, column=0, pady=15, sticky="ew")
        self.stats_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(self.stats_frame, mode="determinate", height=6, progress_color="#00A859")
        self.progress_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.progress_bar.set(0)

        self.stats_label = ctk.CTkLabel(self.stats_frame, text="Ready to Play", font=ctk.CTkFont(size=12), text_color="#AAAAAA")
        self.stats_label.grid(row=1, column=0, pady=(3,0), sticky="w")
        
        self.speed_label = ctk.CTkLabel(self.stats_frame, text="", font=ctk.CTkFont(size=12), text_color="#AAAAAA")
        self.speed_label.grid(row=1, column=1, pady=(3,0), sticky="e")

        self.play_button = PremiumButton(
            self.main_container, 
            text="PLAY", 
            command=self.on_play_click,
            variant="success",
            height=50,
            width=220
        )
        self.play_button.grid(row=3, column=0, pady=20)

        self.log_box = ctk.CTkTextbox(self, fg_color="transparent", text_color="#888888", font=ctk.CTkFont(size=11), height=80, corner_radius=0)
        self.log_box.place(relx=0.5, rely=0.9, anchor="center", relwidth=0.9)
        self.log_box.insert("0.0", "Welcome to the Custom Minecraft Launcher.\n")
        self.log_box.configure(state="disabled")
        
        self.vanilla_versions = []
        threading.Thread(target=self.fetch_versions, daemon=True).start()

        self.download_start_time = 0
        self.downloaded_bytes = 0
        self.max_bytes = 0

    def open_mods_folder(self):
        selected_version = self.version_var.get()
        if not selected_version or selected_version in ["Loading...", "No versions installed"]:
            self.log("No valid version selected for mods folder.")
            return

        minecraft_dir = config.get("minecraft_dir")
        path = os.path.join(minecraft_dir, "profiles", selected_version, "mods")
        
        try:
            os.makedirs(path, exist_ok=True)
            if os.name == 'nt':
                os.startfile(path)
            elif os.name == 'posix':
                subprocess.call(['open', path])
        except Exception as e:
            self.log(f"Error opening mods folder: {e}")

    def update_username(self, value):
        if value:
            config.set("username", value)

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", str(message) + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def fetch_versions(self):
        installed = get_installed_versions()
        if installed:
            self.master.after(0, self.update_version_menu, installed)
        else:
            self.master.after(0, self.update_version_menu, ["No versions installed"])

    def update_version_menu(self, versions):
        if versions:
            self.version_menu.configure(values=versions)
            saved_ver = config.get("selected_version")
            if saved_ver and saved_ver in versions:
                self.version_var.set(saved_ver)
            else:
                self.version_var.set(versions[0])
                config.set("selected_version", versions[0])
        else:
            self.version_menu.configure(values=["None"])
            self.version_var.set("None")

    def on_version_change(self, selected_version):
        config.set("selected_version", selected_version)

    def on_version_change(self, selected_version):
        config.set("selected_version", selected_version)

    def set_max_progress(self, max_progress):
        self.max_bytes = max_progress
        self.downloaded_bytes = 0
        self.download_start_time = time.time()
        self.master.after(0, self.progress_bar.set, 0)
        self.master.after(0, lambda: self.stats_label.configure(text="Starting download..."))
        self.master.after(0, lambda: self.speed_label.configure(text=""))

    def update_progress(self, progress):
        if isinstance(progress, int) or isinstance(progress, float):
            current_bytes = progress
            if self.max_bytes > 0:
                val = current_bytes / self.max_bytes
                self.master.after(0, self.progress_bar.set, val)
                
                elapsed = time.time() - self.download_start_time
                if elapsed > 0:
                    speed_bps = current_bytes / elapsed
                    speed_mbps = speed_bps / (1024 * 1024)
                    
                    remaining_bytes = self.max_bytes - current_bytes
                    eta_seconds = remaining_bytes / speed_bps if speed_bps > 0 else 0
                    
                    mb_downloaded = current_bytes / (1024 * 1024)
                    mb_total = self.max_bytes / (1024 * 1024)
                    
                    stats_text = f"{mb_downloaded:.1f} MB / {mb_total:.1f} MB"
                    speed_text = f"{speed_mbps:.1f} MB/s | ETA: {int(eta_seconds)}s"

                    if int(current_bytes) % 1024 == 0 or current_bytes == self.max_bytes:
                        self.master.after(0, lambda: self.stats_label.configure(text=stats_text))
                        self.master.after(0, lambda: self.speed_label.configure(text=speed_text))

    def on_play_click(self):
        self.play_button.configure(state="disabled", text="LAUNCHING...")
        selected_version = self.version_var.get()
        
        if not selected_version or selected_version in ["Loading...", "No versions installed"]:
            self.log("No valid version selected.")
            self.play_button.configure(state="normal", text="PLAY")
            return

        update_discord_rpc("Playing Minecraft", f"Version {selected_version}")

        def process_launch():
            try:
                self.master.after(0, self.log, f"Launching {selected_version}...")
                self.master.after(0, lambda: self.stats_label.configure(text="Game starting..."))
                self.master.after(0, lambda: self.speed_label.configure(text=""))
                self.master.after(0, self.progress_bar.set, 1)

                launch_callbacks = {
                    "log": lambda msg: self.master.after(0, self.log, msg),
                    "finished": lambda rc: self.master.after(0, self.on_launch_finished, rc)
                }
                launch_minecraft(selected_version, launch_callbacks)
                
            except Exception as e:
                self.master.after(0, self.log, f"Error: {e}")
                self.master.after(0, lambda: self.play_button.configure(state="normal", text="PLAY"))

        threading.Thread(target=process_launch, daemon=True).start()

    def on_launch_finished(self, return_code):
        self.log(f"Minecraft exited with code {return_code}")
        self.play_button.configure(state="normal", text="PLAY")
        self.stats_label.configure(text="Ready")
