import minecraft_launcher_lib
import subprocess
import os
import threading
import pypresence

RPC_CLIENT_ID = "120000000000000000" # Placeholder Client ID
rpc = None

def init_discord_rpc():
    global rpc
    try:
        if rpc is None:
            rpc = pypresence.Presence(RPC_CLIENT_ID)
            rpc.connect()
            rpc.update(state="In Launcher", details="Ready to Play", large_image="minecraft")
    except:
        pass # Ignore failure if Discord isn't running

def update_discord_rpc(state, details):
    global rpc
    try:
        if rpc:
            rpc.update(state=state, details=details, large_image="minecraft")
    except:
        pass
from config.manager import config

def launch_minecraft(version_id, callback_dict=None):
    """
    Generates the launch options and starts the Minecraft process.
    Runs asynchronously to avoid blocking the UI.
    To support both Vanilla and Fabric, pass the appropriate version_id.
    """
    def run_process():
        minecraft_directory = config.get("minecraft_dir")
        username = config.get("username")
        ram_mb = config.get("ram_mb")
        jvm_arguments_str = config.get("jvm_arguments")
        java_path = config.get("java_path")

        # Parsing extra JVM arguments from string
        # Default empty if string is empty
        jvm_args_list = jvm_arguments_str.split() if jvm_arguments_str else []

        # Setting up launch options
        options = {
            "username": username,
            "uuid": "", # Used for offline mode
            "token": "", # Used for offline mode
            "jvmArguments": jvm_args_list + [f"-Xmx{ram_mb}M", f"-Xms{ram_mb}M"],
            "gameDirectory": os.path.join(minecraft_directory, "profiles", version_id),
            "launcherName": "CustomPythonLauncher",
            "launcherVersion": "1.0",
        }

        if java_path and os.path.exists(java_path):
            options["executablePath"] = java_path

        # Emit log message via callback if available
        if callback_dict and 'log' in callback_dict:
            callback_dict['log'](f"Generating launch command for {version_id}...")

        try:
            command = minecraft_launcher_lib.command.get_minecraft_command(version_id, minecraft_directory, options)
            
            if callback_dict and 'log' in callback_dict:
                callback_dict['log']("Starting process...")
                
            # Execute process
            
            # Use specific startup info to hide console window on windows if possible
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                startupinfo=startupinfo,
                text=True # Decode stdout/stderr
            )

            # Signal that process started
            if callback_dict and 'started' in callback_dict:
                callback_dict['started']()

            # Read stdout line by line
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    if callback_dict and 'log' in callback_dict:
                        callback_dict['log'](output.strip())
                        
            # Wait for process to finish
            rc = process.poll()
            
            if callback_dict and 'finished' in callback_dict:
                callback_dict['finished'](rc)

        except Exception as e:
            if callback_dict and 'log' in callback_dict:
                callback_dict['log'](f"Error launching Minecraft: {e}")
            if callback_dict and 'finished' in callback_dict:
                 callback_dict['finished'](-1)
                 
    # Run in a separate thread so we don't block the main application thread (UI)
    thread = threading.Thread(target=run_process)
    thread.daemon = True
    thread.start()
