import customtkinter as ctk
from config.manager import config
from ui.components.inputs import StyledInputRow
from ui.components.buttons import PremiumButton
import ctypes

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedPhys", ctypes.c_ulonglong),
    ]

def get_total_ram_mb():
    try:
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(stat)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        return stat.ullTotalPhys // (1024 * 1024)
    except:
        return 16384 # Fallback to 16GB if failed

class SettingsView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        
        self.header = ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(family="Inter", size=32, weight="bold"))
        self.header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nw")
        
        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.inputs = {}

        self.inputs["username"] = StyledInputRow(
            self.container, 
            "Username", 
            "The name you use in-game (Offline Mode)", 
            config.get("username"), 
            "string"
        )
        self.inputs["username"].pack(fill="x", pady=10)
        
        self.ram_frame = ctk.CTkFrame(self.container, fg_color="#1E1E1E", corner_radius=15)
        self.ram_frame.pack(fill="x", pady=10)
        self.ram_frame.grid_columnconfigure(0, weight=1)

        total_mb = get_total_ram_mb()
        self.max_ram_mb = (total_mb // 1024) * 1024 # Snap to exact GB limit
        if self.max_ram_mb < 2048:
            self.max_ram_mb = 2048 # absolute min floor for testing safety

        current_ram = config.get("ram_mb")
        current_gb = int(current_ram / 1024)
        
        self.ram_label = ctk.CTkLabel(self.ram_frame, text=f"RAM Allocation: {current_gb} GB", font=ctk.CTkFont(size=16, weight="bold"), text_color="#FFFFFF")
        self.ram_label.grid(row=0, column=0, padx=15, pady=(15, 0), sticky="w")
        
        desc = ctk.CTkLabel(self.ram_frame, text=f"Drag memory steps (Available: {int(self.max_ram_mb/1024)} GB)", font=ctk.CTkFont(size=12), text_color="#AAAAAA")
        desc.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")
        
        steps = (self.max_ram_mb - 1024) // 1024
        
        self.ram_slider = ctk.CTkSlider(
            self.ram_frame, 
            from_=1024, 
            to=self.max_ram_mb, 
            number_of_steps=steps if steps > 0 else 1,
            command=self.update_ram_label_text,
            button_color="#00A859",
            button_hover_color="#008044"
        )
        self.ram_slider.set(current_ram)
        self.ram_slider.grid(row=0, column=1, rowspan=2, padx=15, pady=15, sticky="e")
        
        self.inputs["java_path"] = StyledInputRow(
            self.container, 
            "Java Executable Path",
            "Leave empty to use system default java",
            config.get("java_path"),
            "string",
            browse_type="file"
        )
        self.inputs["java_path"].pack(fill="x", pady=10)
        
        self.inputs["jvm_arguments"] = StyledInputRow(
            self.container, 
            "JVM Arguments",
            "Advanced Java arguments",
            config.get("jvm_arguments"),
            "string"
        )
        self.inputs["jvm_arguments"].pack(fill="x", pady=10)

        self.inputs["minecraft_dir"] = StyledInputRow(
            self.container, 
            "Game Directory",
            "Where assets and versions are saved",
            config.get("minecraft_dir"),
            "string",
            browse_type="directory"
        )
        self.inputs["minecraft_dir"].pack(fill="x", pady=10)

        self.save_button = PremiumButton(
            self, 
            text="Save Settings", 
            command=self.save_settings,
            variant="primary"
        )
        self.save_button.grid(row=2, column=0, padx=20, pady=20, sticky="e")

    def update_ram_label_text(self, value):
        mb = int(value / 1024) * 1024
        if mb < 1024:
            mb = 1024 # Floor minimum
        self.ram_label.configure(text=f"RAM Allocation: {mb // 1024} GB")
        self.ram_slider.set(mb)

    def save_settings(self):
        try:
            config.set("username", self.inputs["username"].get())
            config.set("ram_mb", int(self.ram_slider.get()))
            config.set("java_path", self.inputs["java_path"].get())
            config.set("jvm_arguments", self.inputs["jvm_arguments"].get())
            config.set("minecraft_dir", self.inputs["minecraft_dir"].get())
            
            self.save_button.configure(text="Saved!", fg_color="#00A859", hover_color="#008044")
            self.master.after(2000, lambda: self.save_button.configure(
                text="Save Settings", 
                fg_color="#0078D7", 
                hover_color="#005A9E"
            ))
        except ValueError:
            self.save_button.configure(text="Error: Invalid RAM", fg_color="#E81123", hover_color="#B00A1A")
            self.master.after(2000, lambda: self.save_button.configure(
                 text="Save Settings", 
                 fg_color="#0078D7", 
                 hover_color="#005A9E"
            ))

    def update_username_from_home(self):
        self.inputs["username"].set(config.get("username"))
