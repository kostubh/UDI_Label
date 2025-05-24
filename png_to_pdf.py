import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import PyPDF2
from reportlab.pdfgen import canvas
import threading
import time

class PngToPdfConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG to PDF Converter")
        self.root.geometry("600x450")
        self.root.configure(bg="#f0f0f0")
        
        self.selected_files = []
        self.orientation = tk.StringVar(value="portrait")
        self.custom_width = tk.StringVar(value="210")  # Default A4 width in mm
        self.custom_height = tk.StringVar(value="297")  # Default A4 height in mm
        self.is_processing = False
        self.image_size_mm = None  # Store first image size in mm
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="PNG to PDF Converter", font=("Arial", 16, "bold"), bg="#f0f0f0")
        title_label.pack(pady=(0, 20))
        
        # Select files button
        select_button = tk.Button(main_frame, text="Select PNG Images", command=self.select_files, 
                                 font=("Arial", 12), bg="#4CAF50", fg="white", padx=10, pady=5)
        select_button.pack(pady=(0, 10))
        
        # Selected files frame
        self.files_frame = tk.Frame(main_frame, bg="#f0f0f0")
        self.files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.files_label = tk.Label(self.files_frame, text="No files selected", bg="#f0f0f0", font=("Arial", 10))
        self.files_label.pack()
        
        # Page size options frame
        options_frame = tk.Frame(main_frame, bg="#f0f0f0")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Orientation
        orientation_label = tk.Label(options_frame, text="Orientation:", bg="#f0f0f0", font=("Arial", 10, "bold"))
        orientation_label.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        orientations = ["portrait", "landscape"]
        
        for i, orient in enumerate(orientations):
            rb = tk.Radiobutton(options_frame, text=orient.capitalize(), variable=self.orientation, 
                               value=orient, bg="#f0f0f0", font=("Arial", 10))
            rb.grid(row=0, column=i+1, padx=5)
        
        # Custom size frame
        size_frame = tk.Frame(main_frame, bg="#f0f0f0")
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        size_title = tk.Label(size_frame, text="Page Size (mm):", bg="#f0f0f0", font=("Arial", 10, "bold"))
        size_title.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 5))
        
        width_label = tk.Label(size_frame, text="Width:", bg="#f0f0f0", font=("Arial", 10))
        width_label.grid(row=1, column=0, padx=(0, 5), sticky="w")
        
        width_entry = tk.Entry(size_frame, textvariable=self.custom_width, width=8, font=("Arial", 10))
        width_entry.grid(row=1, column=1, padx=(0, 15))
        
        height_label = tk.Label(size_frame, text="Height:", bg="#f0f0f0", font=("Arial", 10))
        height_label.grid(row=1, column=2, padx=(0, 5), sticky="w")
        
        height_entry = tk.Entry(size_frame, textvariable=self.custom_height, width=8, font=("Arial", 10))
        height_entry.grid(row=1, column=3)
        
        # Quick size presets
        presets_frame = tk.Frame(size_frame, bg="#f0f0f0")
        presets_frame.grid(row=2, column=0, columnspan=4, sticky="w", pady=(5, 0))
        
        presets_label = tk.Label(presets_frame, text="Quick presets:", bg="#f0f0f0", font=("Arial", 9))
        presets_label.pack(side=tk.LEFT, padx=(0, 10))
        
        a4_btn = tk.Button(presets_frame, text="A4", command=lambda: self.set_preset(210, 297), 
                          font=("Arial", 8), bg="#e0e0e0", padx=5)
        a4_btn.pack(side=tk.LEFT, padx=2)
        
        letter_btn = tk.Button(presets_frame, text="Letter", command=lambda: self.set_preset(216, 279), 
                              font=("Arial", 8), bg="#e0e0e0", padx=5)
        letter_btn.pack(side=tk.LEFT, padx=2)
        
        # Image size preset button (initially hidden)
        self.image_size_btn = tk.Button(presets_frame, text="Image Size", command=self.set_image_size_preset, 
                                       font=("Arial", 8), bg="#ffeb3b", padx=5)
        # Don't pack initially, will be shown after image selection
        
        # Progress frame
        self.progress_frame = tk.Frame(main_frame, bg="#f0f0f0")
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_label = tk.Label(self.progress_frame, text="", bg="#f0f0f0", font=("Arial", 10))
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate', length=400)
        self.progress_bar.pack(pady=(5, 0))
        
        self.progress_frame.pack_forget()  # Hide initially
        
        # Convert button
        self.convert_button = tk.Button(main_frame, text="Convert to PDF", command=self.start_conversion, 
                                       font=("Arial", 12), bg="#2196F3", fg="white", padx=10, pady=5)
        self.convert_button.pack(pady=(10, 0))
    
    def set_preset(self, width, height):
        self.custom_width.set(str(width))
        self.custom_height.set(str(height))
    
    def set_default_to_image_size(self, width_mm, height_mm):
        # Set default values to image size
        self.custom_width.set(str(width_mm))
        self.custom_height.set(str(height_mm))
        
        # Show and update the image size button
        self.image_size_btn.config(text=f"Image Size ({width_mm}×{height_mm}mm)")
        self.image_size_btn.pack(side=tk.LEFT, padx=2)
    
    def set_image_size_preset(self):
        if self.image_size_mm:
            self.set_preset(self.image_size_mm[0], self.image_size_mm[1])
    
    def select_files(self):
        if self.is_processing:
            messagebox.showwarning("Warning", "Please wait for the current conversion to complete.")
            return
            
        files = filedialog.askopenfilenames(
            title="Select PNG Images",
            filetypes=[("PNG files", "*.png")]
        )
        
        if files:
            self.selected_files = list(files)
            
            # Show progress while checking image sizes
            self.show_progress("Checking image sizes...", 0, len(self.selected_files))
            
            # Use threading to avoid UI freeze
            threading.Thread(target=self.check_image_sizes, daemon=True).start()
    
    def check_image_sizes(self):
        try:
            first_img = Image.open(self.selected_files[0])
            first_size = first_img.size
            same_size = True
            
            # Calculate first image size in mm (assuming 300 DPI)
            dpi = 300  # Default DPI assumption
            if hasattr(first_img, 'info') and 'dpi' in first_img.info:
                dpi = first_img.info['dpi'][0] if isinstance(first_img.info['dpi'], tuple) else first_img.info['dpi']
            
            # Convert pixels to mm (1 inch = 25.4 mm)
            width_mm = round((first_size[0] / dpi) * 25.4, 1)
            height_mm = round((first_size[1] / dpi) * 25.4, 1)
            self.image_size_mm = (width_mm, height_mm)
            
            # Set default values to first image size
            self.root.after(0, lambda: self.set_default_to_image_size(width_mm, height_mm))
            
            for i, file in enumerate(self.selected_files):
                # Update progress
                self.root.after(0, lambda i=i: self.update_progress(i + 1))
                
                if i > 0:  # Skip first image as we already opened it
                    img = Image.open(file)
                    if img.size != first_size:
                        same_size = False
                        # Don't break immediately, let progress complete
                
                # Small delay to prevent overwhelming the system
                if i % 10 == 0:
                    time.sleep(0.01)
            
            # Update UI in main thread
            self.root.after(0, lambda: self.finish_size_check(same_size))
            
        except Exception as e:
            self.root.after(0, lambda: self.handle_error(f"Error checking images: {str(e)}"))
    
    def finish_size_check(self, same_size):
        self.hide_progress()
        
        if not same_size:
            messagebox.showwarning("Warning", "Not all images are the same size. The PDF will be created, but images might be resized.")
        
        # Update the UI to show selected files
        if len(self.selected_files) <= 5:
            files_text = "\n".join([os.path.basename(f) for f in self.selected_files])
        else:
            files_text = "\n".join([os.path.basename(f) for f in self.selected_files[:3]])
            files_text += f"\n...and {len(self.selected_files) - 3} more files"
        
        self.files_label.config(text=f"Selected {len(self.selected_files)} files:\n{files_text}")
    
    def show_progress(self, message, current=0, total=100):
        self.progress_label.config(text=message)
        self.progress_bar['maximum'] = total
        self.progress_bar['value'] = current
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        self.root.update()
    
    def update_progress(self, current):
        self.progress_bar['value'] = current
        if hasattr(self.progress_bar, 'maximum'):
            progress_text = f"Processing... ({current}/{int(self.progress_bar['maximum'])})"
            self.progress_label.config(text=progress_text)
        self.root.update()
    
    def hide_progress(self):
        self.progress_frame.pack_forget()
        self.root.update()
    
    def get_page_size(self):
        try:
            width_mm = float(self.custom_width.get())
            height_mm = float(self.custom_height.get())
            
            if width_mm <= 0 or height_mm <= 0:
                raise ValueError("Dimensions must be positive")
                
            # Convert mm to points (1 mm = 2.83465 points)
            width_pt = width_mm * 2.83465
            height_pt = height_mm * 2.83465
            
            if self.orientation.get() == "landscape":
                return (height_pt, width_pt)  # Swap for landscape
            else:
                return (width_pt, height_pt)
                
        except ValueError:
            return None
    
    def start_conversion(self):
        if self.is_processing:
            messagebox.showwarning("Warning", "Conversion is already in progress.")
            return
            
        if not self.selected_files:
            messagebox.showerror("Error", "No files selected")
            return
        
        page_size = self.get_page_size()
        if page_size is None:
            messagebox.showerror("Error", "Please enter valid positive numbers for width and height")
            return
        
        # Ask user where to save the PDF
        output_file = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not output_file:
            return
        
        # Start conversion in separate thread
        self.is_processing = True
        self.convert_button.config(state=tk.DISABLED, text="Converting...")
        
        threading.Thread(target=self.convert_to_pdf, args=(output_file, page_size), daemon=True).start()
    
    def convert_to_pdf(self, output_file, page_size):
        try:
            self.root.after(0, lambda: self.show_progress("Starting conversion...", 0, len(self.selected_files)))
            
            # Create temporary PDFs for each image
            temp_pdfs = []
            
            for i, img_path in enumerate(self.selected_files):
                # Update progress
                progress_msg = f"Processing image {i+1} of {len(self.selected_files)}"
                self.root.after(0, lambda msg=progress_msg, curr=i+1: self.show_progress(msg, curr, len(self.selected_files)))
                
                temp_pdf = f"temp_{i}_{int(time.time())}.pdf"
                temp_pdfs.append(temp_pdf)
                
                img = Image.open(img_path)
                
                # Calculate scaling to fit the page while maintaining aspect ratio
                img_ratio = img.width / img.height
                page_ratio = page_size[0] / page_size[1]
                
                if img_ratio > page_ratio:  # Image is wider than the page
                    width = page_size[0]
                    height = width / img_ratio
                else:  # Image is taller than the page
                    height = page_size[1]
                    width = height * img_ratio
                
                # Create a new PDF with reportlab
                c = canvas.Canvas(temp_pdf, pagesize=page_size)
                # Calculate centering position
                x_pos = (page_size[0] - width) / 2
                y_pos = (page_size[1] - height) / 2
                c.drawImage(img_path, x_pos, y_pos, width=width, height=height)
                c.save()
                
                # Small delay to prevent overwhelming the system
                if i % 5 == 0:
                    time.sleep(0.01)
            
            # Merge all temporary PDFs
            self.root.after(0, lambda: self.show_progress("Merging PDFs...", 0, 100))
            
            merger = PyPDF2.PdfMerger()
            for i, pdf in enumerate(temp_pdfs):
                merger.append(pdf)
                # Update merge progress
                progress = int((i + 1) / len(temp_pdfs) * 100)
                self.root.after(0, lambda p=progress: self.show_progress("Merging PDFs...", p, 100))
            
            merger.write(output_file)
            merger.close()
            
            # Clean up temporary files
            for pdf in temp_pdfs:
                if os.path.exists(pdf):
                    os.remove(pdf)
            
            # Success message
            self.root.after(0, lambda: self.conversion_complete(output_file))
            
        except Exception as e:
            self.root.after(0, lambda: self.handle_error(f"An error occurred: {str(e)}"))
    
    def conversion_complete(self, output_file):
        self.hide_progress()
        self.is_processing = False
        self.convert_button.config(state=tk.NORMAL, text="Convert to PDF")
        messagebox.showinfo("Success", f"PDF created successfully!\n{os.path.basename(output_file)}")
    
    def handle_error(self, error_message):
        self.hide_progress()
        self.is_processing = False
        self.convert_button.config(state=tk.NORMAL, text="Convert to PDF")
        messagebox.showerror("Error", error_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = PngToPdfConverter(root)
    root.mainloop()