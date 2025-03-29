import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import subprocess

def select_input_file():
    path = filedialog.askopenfilename(title="Select video file")
    if path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, path)

def select_input_dir():
    path = filedialog.askdirectory(title="Select input directory")
    if path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, path)

def select_output_dir():
    initial_dir = os.getcwd()  # Default to the current working directory
    path = filedialog.askdirectory(title="Select output project directory", initialdir=initial_dir)
    if path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, path)

def select_js_file():
    path = filedialog.askopenfilename(title="Select js file")
    if path:
        js_entry.config(state='normal')
        js_entry.delete(0, tk.END)
        js_entry.insert(0, path)
        js_entry.config(state='readonly')

def select_config_file():
    path = filedialog.askopenfilename(title="Select config file")
    if path:
        config_entry.delete(0, tk.END)
        config_entry.insert(0, path)

def toggle_rescale_z():
    if rescale_z_var.get():
        min_z_entry.config(state='normal')
        max_z_entry.config(state='normal')
    else:
        min_z_entry.config(state='disabled')
        max_z_entry.config(state='disabled')

def get_settings():
    data = {}
    data['input_vid'] = input_entry.get()
    data['project_dir'] = output_entry.get()
    try:
        data['nth_frame'] = int(nth_frame_entry.get())
    except ValueError:
        messagebox.showerror("Error", "nth_frame must be an integer.")
        return None
    data['js_path'] = js_entry.get()
    
    data['rescale_z'] = bool(rescale_z_var.get())
    min_z_val = min_z_entry.get().strip()
    max_z_val = max_z_entry.get().strip()
    data['min_z'] = int(min_z_val) if min_z_val != "" else None
    data['max_z'] = int(max_z_val) if max_z_val != "" else None

    data['ori'] = bool(ori_var.get())
    data['sfm'] = sfm_var.get()  # selected from dropdown
    data['prefix'] = prefix_entry.get()
    data['config_file'] = config_entry.get()
    
    # New settings for hemispheres:
    data['north_hem'] = bool(north_hem_var.get())
    data['west_hem'] = bool(west_hem_var.get())
    
    data['clean_up'] = bool(clean_up_var.get())
    return data

def save_pipeline():
    data = get_settings()
    if not data:
        return
    if not data['input_vid'] or not data['project_dir']:
        messagebox.showerror("Error", "Please select both an input video/directory and an output project directory.")
        return
    save_path = filedialog.asksaveasfilename(title="Save Pipeline JSON",
                                               defaultextension=".json",
                                               filetypes=[("JSON files", "*.json")])
    if save_path:
        with open(save_path, "w") as f:
            json.dump(data, f, indent=4)
        messagebox.showinfo("Success", f"Pipeline saved to {save_path}")

def run_pipeline():
    data = get_settings()
    if not data:
        return
    if not data['input_vid'] or not data['project_dir']:
        messagebox.showerror("Error", "Please select both an input video/directory and an output project directory.")
        return
    temp_json = "temp_pipeline_settings.json"
    with open(temp_json, "w") as f:
        json.dump(data, f, indent=4)
    try:
        subprocess.run(["python", "gfam_exec.py", "-i", temp_json], check=True)
        messagebox.showinfo("Success", "Pipeline executed successfully.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Pipeline execution failed: {e}")

def load_pipeline():
    load_path = filedialog.askopenfilename(title="Load Pipeline JSON", filetypes=[("JSON files", "*.json")])
    if load_path:
        try:
            with open(load_path, "r") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON file: {e}")
            return
        
        input_entry.delete(0, tk.END)
        input_entry.insert(0, data.get('input_vid', ''))
        
        output_entry.delete(0, tk.END)
        output_entry.insert(0, data.get('project_dir', ''))
        
        nth_frame_entry.delete(0, tk.END)
        nth_frame_entry.insert(0, str(data.get('nth_frame', '')))
        
        js_entry.config(state='normal')
        js_entry.delete(0, tk.END)
        js_entry.insert(0, data.get('js_path', ''))
        js_entry.config(state='readonly')
        
        rescale_z_var.set(1 if data.get('rescale_z', False) else 0)
        toggle_rescale_z()
        
        min_z_entry.delete(0, tk.END)
        if data.get('min_z') is not None:
            min_z_entry.insert(0, str(data.get('min_z')))
        
        max_z_entry.delete(0, tk.END)
        if data.get('max_z') is not None:
            max_z_entry.insert(0, str(data.get('max_z')))
        
        ori_var.set(1 if data.get('ori', False) else 0)
        sfm_var.set(data.get('sfm', "P4D"))
        
        prefix_entry.delete(0, tk.END)
        prefix_entry.insert(0, data.get('prefix', ''))
        
        config_entry.delete(0, tk.END)
        config_entry.insert(0, data.get('config_file', ''))
        
        # Load hemisphere settings
        north_hem_var.set(1 if data.get('north_hem', False) else 0)
        west_hem_var.set(1 if data.get('west_hem', False) else 0)
        
        clean_up_var.set(1 if data.get('clean_up', False) else 0)
        
        messagebox.showinfo("Loaded", "Pipeline settings loaded successfully.")

# Create the main window
root = tk.Tk()
root.title("GFAM Pipeline Editor")

# Row 0: Input Video/Directory
tk.Label(root, text="Input Video/Directory:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
tk.Button(root, text="Select File", command=select_input_file).grid(row=0, column=3, padx=5, pady=5)
tk.Button(root, text="Select Dir", command=select_input_dir).grid(row=0, column=4, padx=5, pady=5)
tk.Label(root, text="Select the video file or directory to process.").grid(row=0, column=5, sticky="w", padx=5, pady=5)

# Row 1: Output Project Directory
tk.Label(root, text="Output Project Directory:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
tk.Button(root, text="Select Dir", command=select_output_dir).grid(row=1, column=3, padx=5, pady=5)
tk.Label(root, text="Directory where project files will be saved.").grid(row=1, column=5, sticky="w", padx=5, pady=5)

# Row 2: nth_frame
tk.Label(root, text="nth_frame:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
nth_frame_entry = tk.Entry(root)
nth_frame_entry.grid(row=2, column=1, padx=5, pady=5)
tk.Label(root, text="Process every nth frame (integer, e.g., 10).").grid(row=2, column=5, sticky="w", padx=5, pady=5)

# Row 3: js_path selection (read-only with a file select button)
tk.Label(root, text="js_path:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
js_entry = tk.Entry(root, width=50, state='readonly')
js_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=5)
tk.Button(root, text="Select File", command=select_js_file).grid(row=3, column=3, padx=5, pady=5)
tk.Label(root, text="Path to the JavaScript file to be used.").grid(row=3, column=5, sticky="w", padx=5, pady=5)

# Row 4: Rescale Z checkbox
rescale_z_var = tk.IntVar()
tk.Label(root, text="Rescale Z:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
tk.Checkbutton(root, variable=rescale_z_var, command=toggle_rescale_z).grid(row=4, column=1, sticky="w", padx=5, pady=5)
tk.Label(root, text="Enable rescaling of Z axis. When checked, min and max Z become editable.").grid(row=4, column=5, sticky="w", padx=5, pady=5)

# Row 5: min_z
tk.Label(root, text="min_z (empty for default):").grid(row=5, column=0, sticky="e", padx=5, pady=5)
min_z_entry = tk.Entry(root)
min_z_entry.grid(row=5, column=1, padx=5, pady=5)
tk.Label(root, text="Set minimum Z value if rescaling is enabled.").grid(row=5, column=5, sticky="w", padx=5, pady=5)

# Row 6: max_z
tk.Label(root, text="max_z (empty for default):").grid(row=6, column=0, sticky="e", padx=5, pady=5)
max_z_entry = tk.Entry(root)
max_z_entry.grid(row=6, column=1, padx=5, pady=5)
tk.Label(root, text="Set maximum Z value if rescaling is enabled.").grid(row=6, column=5, sticky="w", padx=5, pady=5)

# Row 7: Orientation checkbox
ori_var = tk.IntVar()
tk.Label(root, text="Use orientation:").grid(row=7, column=0, sticky="e", padx=5, pady=5)
tk.Checkbutton(root, variable=ori_var).grid(row=7, column=1, sticky="w", padx=5, pady=5)
tk.Label(root, text="Toggle export of orientation data (IMU for P4D, gravity vector for RC).").grid(row=7, column=5, sticky="w", padx=5, pady=5)

# Row 8: SFM dropdown (OptionMenu)
tk.Label(root, text="SFM:").grid(row=8, column=0, sticky="e", padx=5, pady=5)
sfm_var = tk.StringVar(root)
sfm_var.set("P4D")  # default value
sfm_options = ["P4D", "RC"]
sfm_menu = tk.OptionMenu(root, sfm_var, *sfm_options)
sfm_menu.grid(row=8, column=1, padx=5, pady=5, sticky="w")
tk.Label(root, text="Select SFM (Structure-from-Motion) method.").grid(row=8, column=5, sticky="w", padx=5, pady=5)

# Row 9: Prefix
tk.Label(root, text="Prefix:").grid(row=9, column=0, sticky="e", padx=5, pady=5)
prefix_entry = tk.Entry(root)
prefix_entry.grid(row=9, column=1, padx=5, pady=5)
tk.Label(root, text="Optional prefix for naming outputs.").grid(row=9, column=5, sticky="w", padx=5, pady=5)

# Row 10: Config file selection
tk.Label(root, text="Config File:").grid(row=10, column=0, sticky="e", padx=5, pady=5)
config_entry = tk.Entry(root, width=50)
config_entry.grid(row=10, column=1, columnspan=2, padx=5, pady=5)
tk.Button(root, text="Select File", command=select_config_file).grid(row=10, column=3, padx=5, pady=5)
tk.Label(root, text="Select a configuration file for custom EXIF tags (i.e. Pix4D).").grid(row=10, column=5, sticky="w", padx=5, pady=5)

# Row 11: Clean up checkbox
clean_up_var = tk.IntVar()
tk.Label(root, text="Clean up:").grid(row=11, column=0, sticky="e", padx=5, pady=5)
tk.Checkbutton(root, variable=clean_up_var).grid(row=11, column=1, sticky="w", padx=5, pady=5)
tk.Label(root, text="Remove temporary files after processing.").grid(row=11, column=5, sticky="w", padx=5, pady=5)

# Row 12: Northern Hemisphere and Western Hemisphere checkboxes
north_hem_var = tk.IntVar(value=1)
west_hem_var = tk.IntVar(value=1)
tk.Label(root, text="Hemisphere Settings:").grid(row=12, column=0, sticky="e", padx=5, pady=5)
tk.Checkbutton(root, text="Northern Hemisphere", variable=north_hem_var).grid(row=12, column=1, sticky="w", padx=5, pady=5)
tk.Checkbutton(root, text="Western Hemisphere", variable=west_hem_var).grid(row=12, column=2, sticky="w", padx=5, pady=5)
tk.Label(root, text="Check to set hemisphere parameters. Leave unchecked for other hemisphere.").grid(row=12, column=5, sticky="w", padx=5, pady=5)

# Row 13: Buttons for Load, Save Pipeline and Run Pipeline
tk.Button(root, text="Load Pipeline", command=load_pipeline).grid(row=13, column=0, pady=10)
tk.Button(root, text="Save Pipeline", command=save_pipeline).grid(row=13, column=1, pady=10)
tk.Button(root, text="Run Pipeline", command=run_pipeline).grid(row=13, column=2, pady=10)
tk.Label(root, text="Use these buttons to load, save, or run the pipeline.").grid(row=13, column=5, sticky="w", padx=5, pady=10)

# Initialize rescale Z entries as disabled if not checked
toggle_rescale_z()

root.mainloop()
