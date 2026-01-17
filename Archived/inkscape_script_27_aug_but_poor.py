def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()  # Update the clipboard
        except Exception:
            pass  # Silently fail if clipboard access is not available
import os
import subprocess
import xml.etree.ElementTree as ET
import base64
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading
import time
import webbrowser
import json

CONFIG_FILE = "inkscape_label_gui_config.json"

class InkscapeLabelGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Inkscape Label Generator")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        self.is_processing = False
        self.svg_path = None
        self.temp_svg = "temp_label.svg"
        self.output_folder = "output_pngs"
        self.datamatrix_folder = None
        self.secondary_barcode_folder = None
        self.preview_path = None
        self.config = {}
        self.load_config()
        self.setup_ui()
        self.load_ui_from_config()
    
    def setup_ui(self):
        # Main frame with scrollbar
        main_canvas = tk.Canvas(self.root, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg="#f0f0f0")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title_label = tk.Label(scrollable_frame, text="Inkscape Label Generator", 
                             font=("Arial", 16, "bold"), bg="#f0f0f0")
        title_label.pack(pady=(20, 20))
        
        # SVG Template Selection
        svg_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
        svg_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        svg_label = tk.Label(svg_frame, text="SVG Template:", bg="#f0f0f0", 
                           font=("Arial", 10, "bold"))
        svg_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.svg_path_var = tk.StringVar()
        svg_entry = tk.Entry(svg_frame, textvariable=self.svg_path_var, width=50, 
                           font=("Arial", 10))
        svg_entry.grid(row=1, column=0, padx=(0, 10), sticky="ew")
        
        browse_button = tk.Button(svg_frame, text="Browse", command=self.browse_svg,
                                font=("Arial", 10), bg="#4CAF50", fg="white", padx=10)
        browse_button.grid(row=1, column=1, padx=(0, 10))
        
        # SVG Editor buttons
        editor_frame = tk.Frame(svg_frame, bg="#f0f0f0")
        editor_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        notepad_button = tk.Button(editor_frame, text="Open in Notepad++", 
                                 command=self.open_in_notepad,
                                 font=("Arial", 9), bg="#2196F3", fg="white", padx=5)
        notepad_button.pack(side=tk.LEFT, padx=(0, 5))
        
        inkscape_button = tk.Button(editor_frame, text="Open in Inkscape", 
                                  command=self.open_in_inkscape,
                                  font=("Arial", 9), bg="#2196F3", fg="white", padx=5)
        inkscape_button.pack(side=tk.LEFT)
        
        # Serial Number Prefix
        prefix_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
        prefix_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        prefix_label = tk.Label(prefix_frame, text="Serial Number Prefix:", 
                              bg="#f0f0f0", font=("Arial", 10, "bold"))
        prefix_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.serial_prefix_var = tk.StringVar()
        prefix_entry = tk.Entry(prefix_frame, textvariable=self.serial_prefix_var, 
                              width=20, font=("Arial", 10))
        prefix_entry.grid(row=1, column=0, sticky="w")
        prefix_entry.insert(0, "2506ZLD60XSW")
        
        # Text Replacement Note
        note_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
        note_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        note_label = tk.Label(note_frame, text="Note:", bg="#f0f0f0", 
                            font=("Arial", 10, "bold"))
        note_label.pack(anchor="w")
        
        note_text = tk.Label(note_frame, 
                           text="Any text containing 'serial_number_text' in the SVG file will be replaced with the actual serial number.",
                           bg="#f0f0f0", font=("Arial", 9), fg="#666666", wraplength=700, justify="left")
        note_text.pack(anchor="w", pady=(2, 0))
        
        # DataMatrix Images Folder Selection
        datamatrix_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
        datamatrix_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        datamatrix_label = tk.Label(datamatrix_frame, text="DataMatrix Images Folder:", 
                                  bg="#f0f0f0", font=("Arial", 10, "bold"))
        datamatrix_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.datamatrix_folder_var = tk.StringVar()
        datamatrix_entry = tk.Entry(datamatrix_frame, textvariable=self.datamatrix_folder_var, 
                                  width=50, font=("Arial", 10))
        datamatrix_entry.grid(row=1, column=0, padx=(0, 10), sticky="ew")
        
        datamatrix_browse_button = tk.Button(datamatrix_frame, text="Browse", 
                                           command=self.browse_datamatrix_folder,
                                           font=("Arial", 10), bg="#4CAF50", fg="white", 
                                           padx=10)
        datamatrix_browse_button.grid(row=1, column=1, padx=(0, 10))
        
        # Secondary Barcode Option
        secondary_barcode_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
        secondary_barcode_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.use_secondary_barcode = tk.BooleanVar()
        secondary_checkbox = tk.Checkbutton(secondary_barcode_frame, 
                                          text="Use Secondary Barcode Images", 
                                          variable=self.use_secondary_barcode,
                                          bg="#f0f0f0", font=("Arial", 10, "bold"),
                                          command=self.toggle_secondary_barcode)
        secondary_checkbox.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Secondary barcode folder (initially hidden)
        self.secondary_folder_frame = tk.Frame(secondary_barcode_frame, bg="#f0f0f0")
        
        secondary_folder_label = tk.Label(self.secondary_folder_frame, 
                                        text="Secondary Barcode Images Folder:", 
                                        bg="#f0f0f0", font=("Arial", 10))
        secondary_folder_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.secondary_barcode_folder_var = tk.StringVar()
        secondary_folder_entry = tk.Entry(self.secondary_folder_frame, 
                                        textvariable=self.secondary_barcode_folder_var, 
                                        width=40, font=("Arial", 10))
        secondary_folder_entry.grid(row=1, column=0, padx=(0, 10), sticky="ew")
        
        secondary_browse_button = tk.Button(self.secondary_folder_frame, text="Browse", 
                                          command=self.browse_secondary_barcode_folder,
                                          font=("Arial", 10), bg="#4CAF50", fg="white", 
                                          padx=10)
        secondary_browse_button.grid(row=1, column=1)
        
        # Secondary barcode image ID
        secondary_id_label = tk.Label(self.secondary_folder_frame, 
                                    text="Secondary Barcode Image ID:", 
                                    bg="#f0f0f0", font=("Arial", 10))
        secondary_id_label.grid(row=2, column=0, sticky="w", pady=(5, 0))
        
        self.secondary_image_id = tk.Entry(self.secondary_folder_frame, width=20, 
                                         font=("Arial", 10))
        self.secondary_image_id.insert(0, "image2")
        self.secondary_image_id.grid(row=3, column=0, sticky="w")
        
        # Primary Image ID
        image_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
        image_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        image_label = tk.Label(image_frame, text="Primary Image ID:", bg="#f0f0f0", 
                             font=("Arial", 10, "bold"))
        image_label.grid(row=0, column=0, padx=(0, 5), sticky="w")
        
        self.image_id = tk.Entry(image_frame, width=20, font=("Arial", 10))
        self.image_id.insert(0, "image1")
        self.image_id.grid(row=0, column=1)
        
        # Background Option
        bg_option_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
        bg_option_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.transparent_bg = tk.BooleanVar(value=True)
        transparent_checkbox = tk.Checkbutton(bg_option_frame, 
                                            text="Transparent Background (unchecked = white)", 
                                            variable=self.transparent_bg,
                                            bg="#f0f0f0", font=("Arial", 10, "bold"))
        transparent_checkbox.pack(anchor="w")
        
        # Range inputs
        range_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
        range_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        start_label = tk.Label(range_frame, text="Start Number:", bg="#f0f0f0", 
                             font=("Arial", 10))
        start_label.grid(row=0, column=0, padx=(0, 5), sticky="w")
        
        self.start_number = tk.Entry(range_frame, width=8, font=("Arial", 10))
        self.start_number.grid(row=0, column=1, padx=(0, 15))
        self.start_number.insert(0, "2643")
        
        end_label = tk.Label(range_frame, text="End Number:", bg="#f0f0f0", 
                           font=("Arial", 10))
        end_label.grid(row=0, column=2, padx=(0, 5), sticky="w")
        
        self.end_number = tk.Entry(range_frame, width=8, font=("Arial", 10))
        self.end_number.grid(row=0, column=3)
        self.end_number.insert(0, "3050")
        
        # Progress frame
        self.progress_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
        self.progress_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.progress_label = tk.Label(self.progress_frame, text="", bg="#f0f0f0", 
                                     font=("Arial", 10))
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate', 
                                          length=400)
        self.progress_bar.pack(pady=(5, 0))
        
        self.progress_frame.pack_forget()  # Hide initially
        
        # Generate button
        self.generate_button = tk.Button(scrollable_frame, text="Generate Labels", 
                                       command=self.start_generation,
                                       font=("Arial", 12), bg="#2196F3", fg="white", 
                                       padx=10, pady=5)
        self.generate_button.pack(pady=(10, 0))
        
        # Preview frame (only button, no image)
        preview_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
        preview_frame.pack(fill=tk.X, padx=20, pady=(20, 20))
        
        preview_label = tk.Label(preview_frame, text="Preview:", bg="#f0f0f0", 
                               font=("Arial", 10, "bold"))
        preview_label.pack(anchor="w", pady=(0, 5))
        
        preview_buttons = tk.Frame(preview_frame, bg="#f0f0f0")
        preview_buttons.pack(side=tk.LEFT, fill=tk.Y)
        
        self.view_button = tk.Button(preview_buttons, text="Open in Viewer", 
                                   command=self.open_preview,
                                   font=("Arial", 10), bg="#4CAF50", fg="white", 
                                   padx=10, pady=5)
        self.view_button.pack(pady=(0, 0))
        self.view_button.config(state=tk.DISABLED)
        
        # Pack the main canvas and scrollbar
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def toggle_secondary_barcode(self):
        if self.use_secondary_barcode.get():
            self.secondary_folder_frame.grid(row=1, column=0, sticky="w", pady=(10, 0))
        else:
            self.secondary_folder_frame.grid_forget()
        self.save_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception:
                self.config = {}
        else:
            self.config = {}

    def save_config(self):
        self.config["svg_path"] = self.svg_path_var.get()
        self.config["serial_prefix"] = self.serial_prefix_var.get()
        self.config["datamatrix_folder"] = self.datamatrix_folder_var.get()
        self.config["use_secondary_barcode"] = self.use_secondary_barcode.get()
        self.config["secondary_barcode_folder"] = self.secondary_barcode_folder_var.get()
        self.config["secondary_image_id"] = self.secondary_image_id.get()
        self.config["image_id"] = self.image_id.get()
        self.config["start_number"] = self.start_number.get()
        self.config["end_number"] = self.end_number.get()
        self.config["transparent_bg"] = self.transparent_bg.get()
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def load_ui_from_config(self):
        if self.config.get("svg_path"):
            self.svg_path_var.set(self.config["svg_path"])
            self.svg_path = self.config["svg_path"]
        if self.config.get("serial_prefix"):
            self.serial_prefix_var.set(self.config["serial_prefix"])
        if self.config.get("datamatrix_folder"):
            self.datamatrix_folder_var.set(self.config["datamatrix_folder"])
            self.datamatrix_folder = self.config["datamatrix_folder"]
        if self.config.get("use_secondary_barcode"):
            self.use_secondary_barcode.set(self.config["use_secondary_barcode"])
            self.toggle_secondary_barcode()
        if self.config.get("secondary_barcode_folder"):
            self.secondary_barcode_folder_var.set(self.config["secondary_barcode_folder"])
            self.secondary_barcode_folder = self.config["secondary_barcode_folder"]
        if self.config.get("secondary_image_id"):
            self.secondary_image_id.delete(0, tk.END)
            self.secondary_image_id.insert(0, self.config["secondary_image_id"])
        if self.config.get("image_id"):
            self.image_id.delete(0, tk.END)
            self.image_id.insert(0, self.config["image_id"])
        if self.config.get("start_number"):
            self.start_number.delete(0, tk.END)
            self.start_number.insert(0, self.config["start_number"])
        if self.config.get("end_number"):
            self.end_number.delete(0, tk.END)
            self.end_number.insert(0, self.config["end_number"])
        if "transparent_bg" in self.config:
            self.transparent_bg.set(self.config["transparent_bg"])

    def browse_svg(self):
        file_path = filedialog.askopenfilename(
            title="Select SVG Template",
            filetypes=[("SVG files", "*.svg")]
        )
        if file_path:
            self.svg_path = file_path
            self.svg_path_var.set(file_path)
            self.save_config()
    
    def browse_datamatrix_folder(self):
        folder = filedialog.askdirectory(title="Select DataMatrix Images Folder")
        if folder:
            self.datamatrix_folder = folder
            self.datamatrix_folder_var.set(folder)
            self.save_config()

    def browse_secondary_barcode_folder(self):
        folder = filedialog.askdirectory(title="Select Secondary Barcode Images Folder")
        if folder:
            self.secondary_barcode_folder = folder
            self.secondary_barcode_folder_var.set(folder)
            self.save_config()
    
    def open_in_notepad(self):
        if self.svg_path and os.path.exists(self.svg_path):
            try:
                subprocess.Popen(["start", "notepad++", self.svg_path], shell=True)
            except:
                messagebox.showerror("Error", "Could not open Notepad++. Please make sure it's installed.")
        else:
            messagebox.showwarning("Warning", "Please select an SVG file first.")
    
    def open_in_inkscape(self):
        if self.svg_path and os.path.exists(self.svg_path):
            try:
                subprocess.Popen(["inkscape", self.svg_path])
            except:
                messagebox.showerror("Error", "Could not open Inkscape. Please make sure it's installed.")
        else:
            messagebox.showwarning("Warning", "Please select an SVG file first.")
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()  # Update the clipboard
        except Exception:
            pass  # Silently fail if clipboard access is not available
    
    def show_progress(self, message, current=0, total=100):
        self.progress_label.config(text=message)
        self.progress_bar['maximum'] = total
        self.progress_bar['value'] = current
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        self.root.update()
    
    def update_progress(self, current, total):
        progress = int((current / total) * 100)
        self.progress_bar['value'] = progress
        progress_text = f"Processing... ({current}/{total})"
        self.progress_label.config(text=progress_text)
        self.root.update()
    
    def hide_progress(self):
        self.progress_frame.pack_forget()
        self.root.update()
    
    def start_generation(self):
        if self.is_processing:
            messagebox.showwarning("Warning", "Generation is already in progress.")
            return
        
        if not self.svg_path or not os.path.exists(self.svg_path):
            messagebox.showerror("Error", "Please select a valid SVG template file.")
            return
        
        if not self.datamatrix_folder or not os.path.exists(self.datamatrix_folder):
            messagebox.showerror("Error", "Please select a valid DataMatrix images folder.")
            return
        
        # Check secondary barcode folder if enabled
        if self.use_secondary_barcode.get():
            if not self.secondary_barcode_folder or not os.path.exists(self.secondary_barcode_folder):
                messagebox.showerror("Error", "Please select a valid Secondary Barcode images folder.")
                return
        
        try:
            start = int(self.start_number.get())
            end = int(self.end_number.get())
            
            if start < 1 or end < start:
                messagebox.showerror("Error", "Please enter valid start and end numbers")
                return
            
            # Get element IDs
            image_id = self.image_id.get()
            secondary_image_id = self.secondary_image_id.get() if self.use_secondary_barcode.get() else None
            
            if not image_id:
                messagebox.showerror("Error", "Please enter Primary Image ID")
                return
            
            if self.use_secondary_barcode.get() and not secondary_image_id:
                messagebox.showerror("Error", "Please enter Secondary Barcode Image ID")
                return
            
            # Create output folder
            os.makedirs(self.output_folder, exist_ok=True)
            
            # Save config
            self.save_config()
            
            # Start generation in separate thread
            self.is_processing = True
            self.generate_button.config(state=tk.DISABLED, text="Generating...")
            
            threading.Thread(target=self.generate_labels, 
                           args=(start, end, image_id, secondary_image_id), 
                           daemon=True).start()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for start and end")
            self.is_processing = False
            self.generate_button.config(state=tk.NORMAL, text="Generate Labels")
    
    def generate_labels(self, start, end, image_id, secondary_image_id):
        try:
            total = end - start + 1
            self.root.after(0, lambda: self.show_progress("Starting generation...", 0, total))
            
            # Get serial number prefix
            serial_prefix = self.serial_prefix_var.get()
            
            # Process first image for preview
            first_serial = f"{serial_prefix}{start:04d}"
            self.process_single_label(start, first_serial, image_id, secondary_image_id, True)
            
            # Process remaining images
            for i in range(start + 1, end + 1):
                self.root.after(0, lambda curr=i-start+1: self.update_progress(curr, total))
                serial_number = f"{serial_prefix}{i:04d}"
                self.process_single_label(i, serial_number, image_id, secondary_image_id, False)
                
                # Small delay to prevent overwhelming the system
                if i % 5 == 0:
                    time.sleep(0.01)
            
            # Success message
            self.root.after(0, lambda: self.generation_complete())
            
        except Exception as e:
            self.root.after(0, lambda: self.handle_error(f"An error occurred: {str(e)}"))
    
    def process_single_label(self, index, serial_number, image_id, secondary_image_id, is_preview):
        # Reload SVG each time
        tree = ET.parse(self.svg_path)
        root = tree.getroot()
        
        # Update any text containing "serial_number_text"
        for elem in root.iter():
            if elem.text and "serial_number_text" in elem.text:
                elem.text = elem.text.replace("serial_number_text", serial_number)
        
        # Update primary image (DataMatrix)
        image_path = os.path.join(self.datamatrix_folder, f"{serial_number}.png")
        if not os.path.exists(image_path):
            messagebox.showerror("Error", f"DataMatrix image not found: {image_path}")
            return
        
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
            href_val = f"data:image/png;base64,{img_base64}"
            
            for image_elem in root.iter():
                if image_elem.attrib.get("id") == image_id:
                    image_elem.attrib["{http://www.w3.org/1999/xlink}href"] = href_val
                    break
        
        # Update secondary barcode image if enabled
        if self.use_secondary_barcode.get() and secondary_image_id:
            secondary_image_path = os.path.join(self.secondary_barcode_folder, f"{serial_number}.png")
            if os.path.exists(secondary_image_path):
                with open(secondary_image_path, "rb") as img_file:
                    img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
                    href_val = f"data:image/png;base64,{img_base64}"
                    
                    for image_elem in root.iter():
                        if image_elem.attrib.get("id") == secondary_image_id:
                            image_elem.attrib["{http://www.w3.org/1999/xlink}href"] = href_val
                            break
            else:
                print(f"Warning: Secondary barcode image not found: {secondary_image_path}")
        
        # Write modified SVG
        tree.write(self.temp_svg)
        
        # Export to PNG with transparent or white background based on checkbox
        output_png = os.path.join(self.output_folder, f"label_{serial_number}.png")
        
        if self.transparent_bg.get():
            # Export with transparent background
            subprocess.run([
                "inkscape",
                self.temp_svg,
                "--export-type=png",
                "--export-area-page",
                "--export-dpi=600",
                "--export-filename", output_png
            ])
        else:
            # Export with white background
            subprocess.run([
                "inkscape",
                self.temp_svg,
                "--export-type=png",
                "--export-area-page",
                "--export-dpi=600",
                "--export-background=white",
                "--export-background-opacity=255",
                "--export-filename", output_png
            ])
        
        if is_preview:
            self.preview_path = output_png
            self.view_button.config(state=tk.NORMAL)
    
    def open_preview(self):
        if self.preview_path and os.path.exists(self.preview_path):
            os.startfile(self.preview_path)
    
    def generation_complete(self):
        self.hide_progress()
        self.is_processing = False
        self.generate_button.config(state=tk.NORMAL, text="Generate Labels")
        messagebox.showinfo("Success", "Labels generated successfully!")
    
    def handle_error(self, error_message):
        self.hide_progress()
        self.is_processing = False
        self.generate_button.config(state=tk.NORMAL, text="Generate Labels")
        messagebox.showerror("Error", error_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = InkscapeLabelGenerator(root)
    root.mainloop()