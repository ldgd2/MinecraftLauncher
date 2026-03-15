import customtkinter as ctk
from config.manager import config
import threading
import time
from core.versions import get_available_vanilla_versions, get_available_fabric_versions, install_vanilla_version, install_fabric_version
from ui.components.buttons import PremiumButton

class DownloadsView(ctk.CTkFrame):
    def __init__(self, master, on_download_complete=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_download_complete = on_download_complete
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self.header = ctk.CTkLabel(self, text="Download Versions", font=ctk.CTkFont(family="Inter", size=32, weight="bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nw")
        
        self.version_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=15)
        self.version_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.version_frame.grid_columnconfigure(1, weight=1)
        
        self.type_label = ctk.CTkLabel(self.version_frame, text="Type:", font=ctk.CTkFont(size=14))
        self.type_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.type_var = ctk.StringVar(value="Vanilla")
        self.type_menu = ctk.CTkOptionMenu(
            self.version_frame, 
            variable=self.type_var, 
            values=["Vanilla", "Fabric"],
            command=self.on_type_change,
            fg_color="#333333",
            button_color="#444444",
            button_hover_color="#555555"
        )
        self.type_menu.grid(row=0, column=1, padx=15, pady=15, sticky="ew")
        
        self.version_label = ctk.CTkLabel(self.version_frame, text="Release Version:", font=ctk.CTkFont(size=14))
        self.version_label.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")
        
        self.version_var = ctk.StringVar(value="Loading...")
        self.version_menu = ctk.CTkOptionMenu(
            self.version_frame, 
            variable=self.version_var, 
            values=["Loading..."],
            fg_color="#333333",
            button_color="#444444",
            button_hover_color="#555555"
        )
        self.version_menu.grid(row=1, column=1, padx=15, pady=(0, 15), sticky="ew")
        
        self.log_box = ctk.CTkTextbox(self, fg_color="#1E1E1E", text_color="#AAAAAA", corner_radius=15)
        self.log_box.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.log_box.insert("0.0", "Select a version to download and install.\n")
        self.log_box.configure(state="disabled")

        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        self.action_frame.grid_columnconfigure(0, weight=1)
        
        self.stats_frame = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        self.stats_frame.grid(row=0, column=0, padx=(0, 15), sticky="ew")
        self.stats_frame.grid_columnconfigure(0, weight=1)
        self.stats_frame.grid_columnconfigure(1, weight=1)

        self.progress_bar = ctk.CTkProgressBar(self.stats_frame, mode="determinate", height=10)
        self.progress_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.progress_bar.set(0)

        self.stats_label = ctk.CTkLabel(self.stats_frame, text="Ready", font=ctk.CTkFont(size=12), text_color="#AAAAAA")
        self.stats_label.grid(row=1, column=0, pady=(5,0), sticky="w")
        
        self.speed_label = ctk.CTkLabel(self.stats_frame, text="", font=ctk.CTkFont(size=12), text_color="#AAAAAA")
        self.speed_label.grid(row=1, column=1, pady=(5,0), sticky="e")

        self.download_button = PremiumButton(
            self.action_frame, 
            text="INSTALL", 
            command=self.on_download_click,
            variant="primary",
            width=200
        )
        self.download_button.grid(row=0, column=1, sticky="e")
        
        self.vanilla_versions = []
        threading.Thread(target=self.fetch_versions, daemon=True).start()

        self.download_start_time = 0
        self.downloaded_bytes = 0
        self.max_bytes = 0

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", str(message) + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def fetch_versions(self):
        self.vanilla_versions = get_available_vanilla_versions()
        if self.vanilla_versions:
            self.master.after(0, self.update_version_menu, self.vanilla_versions)
        else:
            self.master.after(0, self.update_version_menu, ["Error fetching versions"])

    def update_version_menu(self, versions):
        if versions:
            self.version_menu.configure(values=versions)
            self.version_var.set(versions[0])
        else:
            self.version_menu.configure(values=["None"])
            self.version_var.set("None")

    def on_type_change(self, selected_type):
        if selected_type == "Vanilla":
            self.update_version_menu(self.vanilla_versions)
        elif selected_type == "Fabric":
            self.update_version_menu(self.vanilla_versions)

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

    def on_download_click(self):
        self.download_button.configure(state="disabled", text="INSTALLING...")
        selected_version = self.version_var.get()
        selected_type = self.type_var.get()
        
        if not selected_version or selected_version in ["Loading...", "Error fetching versions", "None"]:
            self.log("Invalid version selected.")
            self.download_button.configure(state="normal", text="INSTALL")
            return

        def process_download():
            callbacks = {
                "setStatus": lambda summary: self.master.after(0, self.log, summary),
                "setProgress": self.update_progress,
                "setMax": self.set_max_progress,
                "log": lambda msg: self.master.after(0, self.log, msg)
            }
            
            try:
                if selected_type == "Vanilla":
                    self.master.after(0, self.log, f"Downloading Vanilla {selected_version}...")
                    install_vanilla_version(selected_version, callbacks)
                else:
                    self.master.after(0, self.log, f"Fetching latest Fabric loader for {selected_version}...")
                    loaders = get_available_fabric_versions(selected_version)
                    if not loaders:
                        self.master.after(0, self.log, "No fabric loaders found.")
                        self.master.after(0, lambda: self.download_button.configure(state="normal", text="INSTALL"))
                        return
                        
                    loader = loaders[0]
                    self.master.after(0, self.log, f"Downloading Fabric {loader} for {selected_version}...")
                    install_fabric_version(selected_version, loader, callbacks)

                self.master.after(0, self.log, "Download complete!")
                self.master.after(0, lambda: self.download_button.configure(state="normal", text="INSTALL"))
                self.master.after(0, lambda: self.stats_label.configure(text="Installed!"))
                self.master.after(0, lambda: self.speed_label.configure(text=""))
                
                if self.on_download_complete:
                     self.master.after(0, self.on_download_complete)

            except Exception as e:
                self.master.after(0, self.log, f"Error: {e}")
                self.master.after(0, lambda: self.download_button.configure(state="normal", text="INSTALL"))

        threading.Thread(target=process_download, daemon=True).start()
