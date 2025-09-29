import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import threading
import os
import base64
import sys

# --- Global Settings ---
BUNDLE_FILENAME = "bundle.py"
OUTPUT_FILE = "package.zip"
REQUIRED_PACKAGES = ["pyyaml", "requests"] 

FLIPPER_ICON = """
R0lGODlhEAAQAIABAP///wAAACH5BAEKAAEALAAAAAAQABAAAAIjhI+py+0P
VAIkH1jHwFz2oJ4uK57hX6tFq4I5mJ4QBADs=
"""

class FlipperBuilderApp:
    def __init__(self, master):
        self.master = master
        master.title("Flipper Zero App Builder")
        self.set_icon(master) 
        
        self.base_dir = None
        
        tools_frame = tk.Frame(master)
        tools_frame.pack(padx=10, pady=5, fill='x')

        tk.Label(tools_frame, text="Step 1: Select the Project Root Directory (e.g., the folder containing the 'Tools' folder):", font=("Arial", 10)).pack(anchor='w')
        
        self.tools_path = tk.StringVar(master)
        tk.Entry(tools_frame, textvariable=self.tools_path, width=80).pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 5))
        
        tk.Button(tools_frame, text="Select Directory", command=self.browse_base_dir).pack(side=tk.RIGHT)

        manifest_frame = tk.Frame(master)
        manifest_frame.pack(padx=10, pady=5, fill='x')

        tk.Label(manifest_frame, text="Step 2: Select the Application Manifest File (manifest.yml):", font=("Arial", 10)).pack(anchor='w')
        
        self.manifest_path = tk.StringVar(master)
        self.entry = tk.Entry(manifest_frame, textvariable=self.manifest_path, width=80, state=tk.DISABLED)
        self.entry.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 5))
        
        self.browse_manifest_button = tk.Button(manifest_frame, text="Select Manifest (YAML)", command=self.browse_manifest, state=tk.DISABLED)
        self.browse_manifest_button.pack(side=tk.RIGHT)

        self.build_button = tk.Button(master, text="START BUILD (bundle.py)", command=self.run_build, bg="dark green", fg="white", font=("Arial", 12, "bold"), state=tk.DISABLED)
        self.build_button.pack(pady=10)

        tk.Label(master, text="Build Logs:").pack(anchor='w', padx=10, pady=(10, 0))
        self.log_text = tk.Text(master, height=15, width=80, bg="#2b2b2b", fg="#6AAB73") 
        self.log_text.pack(padx=10, pady=10, fill='both', expand=True)

        tk.Label(master, text="Reminder: Manifest IDs must use only lowercase letters, numbers, and underscores!", fg="red").pack(pady=(0, 10))

    def set_icon(self, master):
        try:
            icon_data = base64.b64decode(FLIPPER_ICON)
            icon = tk.PhotoImage(data=icon_data)
            master.iconphoto(True, icon)
        except Exception:
            pass

    def check_and_install_pip(self):
        self.log_text.insert(tk.END, "--- Verifying 'pip' installation ---\n")
        self.log_text.see(tk.END)

        try:
            subprocess.check_output([sys.executable, "-m", "pip", "--version"], stderr=subprocess.STDOUT)
            self.log_text.insert(tk.END, "PIP: 'pip' is already installed and functional.\n")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_text.insert(tk.END, "PIP: 'pip' command not found or failed. Attempting to install 'pip' using ensurepip...\n")
            
            try:
                import ensurepip
                ensurepip.bootstrap() 
                self.log_text.insert(tk.END, "PIP: 'pip' installed successfully using ensurepip!\n")
                return True
            except Exception as e:
                self.log_text.insert(tk.END, f"PIP: Failed to install 'pip' via ensurepip. Error: {e}\n")
                self.log_text.insert(tk.END, "PIP: Please install 'pip' manually using 'python -m ensurepip --default-pip' in your console.\n")
                return False

    def check_and_install_dependencies(self):
        self.log_text.insert(tk.END, "--- Checking required Python packages ---\n")
        self.log_text.see(tk.END)
        
        try:
            install_command = [sys.executable, "-m", "pip", "install"] + REQUIRED_PACKAGES
            
            process = subprocess.Popen(
                install_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            for line in iter(process.stdout.readline, ''):
                self.log_text.insert(tk.END, f"DEP: {line}")
                self.log_text.see(tk.END)
            
            process.wait()
            
            if process.returncode == 0:
                self.log_text.insert(tk.END, "\n--- All dependencies checked and installed successfully. ---\n\n")
                return True
            else:
                self.log_text.insert(tk.END, "\n--- DEPENDENCY INSTALLATION FAILED! Check connection/permissions. ---\n\n")
                return False

        except Exception as e:
            self.log_text.insert(tk.END, f"\n--- ERROR during dependency check: {e} ---\n\n")
            return False

    def browse_base_dir(self):
        directory = filedialog.askdirectory(title="Select the Project Root Directory")
        
        if directory:
            bundle_full_path = os.path.join(directory, "Tools", BUNDLE_FILENAME)
            
            if os.path.exists(bundle_full_path):
                self.tools_path.set(directory)
                self.base_dir = directory
                self.entry.config(state=tk.NORMAL)
                self.browse_manifest_button.config(state=tk.NORMAL)
                self.build_button.config(state=tk.NORMAL)
                messagebox.showinfo("Success", f"Found {BUNDLE_FILENAME} at '{bundle_full_path}'. You can now select the manifest file (Step 2).")
            else:
                self.base_dir = None
                self.tools_path.set("")
                self.entry.config(state=tk.DISABLED)
                self.browse_manifest_button.config(state=tk.DISABLED)
                self.build_button.config(state=tk.DISABLED)
                messagebox.showerror("Path Error", f"Could not find Tools/{BUNDLE_FILENAME} in the selected directory. Please choose the root directory containing the 'Tools' folder.")

    def browse_manifest(self):
        if not self.base_dir:
            messagebox.showerror("Error", "Please select the project's root directory first (Step 1).")
            return
            
        file_path = filedialog.askopenfilename(
            initialdir=os.path.join(self.base_dir, "applications"),
            title="Select Application Manifest File (manifest.yml)",
            filetypes=(("YAML Manifest Files", "manifest.yml"), ("All files", "*.*"))
        )
        
        if file_path:
            try:
                relative_path = os.path.relpath(file_path, self.base_dir).replace('\\', '/')
                self.manifest_path.set(relative_path)
            except ValueError:
                self.manifest_path.set(file_path)
                messagebox.showwarning("Warning", "File selected from a different drive. Full path used, but this might cause relative path issues.")

    def run_build(self):
        manifest = self.manifest_path.get().strip()
        if not self.base_dir or not manifest:
            messagebox.showerror("Error", "Please complete both steps (select directory and manifest).")
            return
            
        self.log_text.delete(1.0, tk.END)
        self.build_button.config(state=tk.DISABLED, text="INITIALIZING...")
        self.browse_manifest_button.config(state=tk.DISABLED)

        thread = threading.Thread(target=self._full_build_process, args=(manifest,))
        thread.start()

    def _full_build_process(self, manifest):
        
        self.master.after(0, self.build_button.config, {'text': "VERIFYING PIP..."})
        
        try:
            if not self.check_and_install_pip():
                self.log_text.insert(tk.END, "BUILD STOPPED: PIP not functional.\n")
                self.master.after(0, messagebox.showerror, "Error", "PIP is not functional. Please install it manually.")
                return

            self.master.after(0, self.build_button.config, {'text': "INSTALLING DEPENDENCIES..."})
            if not self.check_and_install_dependencies():
                self.log_text.insert(tk.END, "BUILD STOPPED: Dependency error.\n")
                self.master.after(0, messagebox.showerror, "Error", "Dependencies could not be installed. Check your internet connection or permissions.")
                return

            self.log_text.insert(tk.END, "STARTING BUILD PROCESS...\n")
            self.master.after(0, self.build_button.config, {'text': "BUILDING..."})

            bundle_script_path = os.path.join("Tools", BUNDLE_FILENAME)
            full_command = ["py", bundle_script_path, "--nolint", manifest, OUTPUT_FILE]
            
            build_successful = False
            
            process = subprocess.Popen(
                full_command,
                cwd=self.base_dir,  
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            for line in iter(process.stdout.readline, ''):
                self.log_text.insert(tk.END, line)
                self.log_text.see(tk.END)
                
                if "Bundle created: package.zip" in line:
                    build_successful = True

            process.wait()
            
            if build_successful and process.returncode == 0:
                self.log_text.insert(tk.END, "\n\n=== BUILD SUCCESSFUL! 🎉 ===\n")
                self.log_text.insert(tk.END, f"Output file created: {os.path.join(self.base_dir, OUTPUT_FILE)}")
                self.master.after(0, messagebox.showinfo, "Success!", "The Flipper Zero application package was created successfully as package.zip! 🎉")
            else:
                self.log_text.insert(tk.END, "\n\n=== BUILD FAILED! ===\n")
                self.master.after(0, messagebox.showerror, "Error", "The build process failed. Please check the logs for details.")

        except Exception as e:
            self.log_text.insert(tk.END, f"\n\nUNEXPECTED ERROR: {e}")
            self.master.after(0, messagebox.showerror, "Error", f"An unexpected error occurred: {e}")
        finally:
            self.master.after(0, self.build_button.config, {'state': tk.NORMAL, 'text': "START BUILD (bundle.py)"})
            self.master.after(0, self.browse_manifest_button.config, {'state': tk.NORMAL})


if __name__ == "__main__":
    root = tk.Tk()
    app = FlipperBuilderApp(root)
    root.mainloop()