import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, landscape, portrait

class PngToPdfConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG to PDF Converter")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f0f0")
        
        self.selected_files = []
        self.page_size = tk.StringVar(value="A4")
        self.orientation = tk.StringVar(value="portrait")
        self.custom_width = tk.StringVar(value="")
        self.custom_height = tk.StringVar(value="")
        
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
        
        # Page size
        size_label = tk.Label(options_frame, text="Page Size:", bg="#f0f0f0", font=("Arial", 10))
        size_label.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        sizes = ["A4", "Letter", "Custom"]
        
        for i, size in enumerate(sizes):
            rb = tk.Radiobutton(options_frame, text=size, variable=self.page_size, value=size, 
                               bg="#f0f0f0", command=self.toggle_custom_size)
            rb.grid(row=0, column=i+1, padx=5)
        
        # Orientation
        orientation_label = tk.Label(options_frame, text="Orientation:", bg="#f0f0f0", font=("Arial", 10))
        orientation_label.grid(row=1, column=0, padx=(0, 10), sticky="w", pady=(10, 0))
        
        orientations = ["portrait", "landscape"]
        
        for i, orient in enumerate(orientations):
            rb = tk.Radiobutton(options_frame, text=orient.capitalize(), variable=self.orientation, value=orient, bg="#f0f0f0")
            rb.grid(row=1, column=i+1, padx=5, pady=(10, 0))
        
        # Custom size frame
        self.custom_frame = tk.Frame(main_frame, bg="#f0f0f0")
        self.custom_frame.pack(fill=tk.X, pady=(0, 10))
        
        width_label = tk.Label(self.custom_frame, text="Width (mm):", bg="#f0f0f0")
        width_label.grid(row=0, column=0, padx=(0, 5), sticky="w")
        
        width_entry = tk.Entry(self.custom_frame, textvariable=self.custom_width, width=8)
        width_entry.grid(row=0, column=1, padx=(0, 15))
        
        height_label = tk.Label(self.custom_frame, text="Height (mm):", bg="#f0f0f0")
        height_label.grid(row=0, column=2, padx=(0, 5), sticky="w")
        
        height_entry = tk.Entry(self.custom_frame, textvariable=self.custom_height, width=8)
        height_entry.grid(row=0, column=3)
        
        self.custom_frame.grid_remove()  # Hide initially
        
        # Convert button
        convert_button = tk.Button(main_frame, text="Convert to PDF", command=self.convert_to_pdf, 
                                  font=("Arial", 12), bg="#2196F3", fg="white", padx=10, pady=5)
        convert_button.pack(pady=(10, 0))
    
    def toggle_custom_size(self):
        if self.page_size.get() == "Custom":
            self.custom_frame.pack(fill=tk.X, pady=(0, 10))
        else:
            self.custom_frame.pack_forget()
    
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select PNG Images",
            filetypes=[("PNG files", "*.png")]
        )
        
        if files:
            self.selected_files = list(files)
            
            # Check if all images are the same size
            first_img = Image.open(self.selected_files[0])
            first_size = first_img.size
            same_size = True
            
            for file in self.selected_files[1:]:
                img = Image.open(file)
                if img.size != first_size:
                    same_size = False
                    break
            
            if not same_size:
                messagebox.showwarning("Warning", "Not all images are the same size. The PDF will be created, but images might be resized.")
            
            # Update the UI to show selected files
            if len(self.selected_files) <= 3:
                files_text = "\n".join([os.path.basename(f) for f in self.selected_files])
            else:
                files_text = "\n".join([os.path.basename(f) for f in self.selected_files[:2]])
                files_text += f"\n...and {len(self.selected_files) - 2} more files"
            
            self.files_label.config(text=f"Selected {len(self.selected_files)} files:\n{files_text}")
    
    def get_page_size(self):
        size_option = self.page_size.get()
        is_landscape = self.orientation.get() == "landscape"
        
        if size_option == "A4":
            size = A4
        elif size_option == "Letter":
            size = letter
        else:  # Custom
            try:
                width_mm = float(self.custom_width.get())
                height_mm = float(self.custom_height.get())
                # Convert mm to points (1 mm = 2.83465 points)
                width_pt = width_mm * 2.83465
                height_pt = height_mm * 2.83465
                size = (width_pt, height_pt)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for width and height")
                return None
        
        if is_landscape and size_option != "Custom":
            return landscape(size)
        else:
            return size if size_option != "Custom" else size
    
    def convert_to_pdf(self):
        if not self.selected_files:
            messagebox.showerror("Error", "No files selected")
            return
        
        page_size = self.get_page_size()
        if page_size is None:
            return
        
        # Ask user where to save the PDF
        output_file = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not output_file:
            return
        
        try:
            # Create temporary PDFs for each image
            temp_pdfs = []
            for i, img_path in enumerate(self.selected_files):
                temp_pdf = f"temp_{i}.pdf"
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
            
            # Merge all temporary PDFs
            merger = PyPDF2.PdfMerger()
            for pdf in temp_pdfs:
                merger.append(pdf)
            
            merger.write(output_file)
            merger.close()
            
            # Clean up temporary files
            for pdf in temp_pdfs:
                if os.path.exists(pdf):
                    os.remove(pdf)
            
            messagebox.showinfo("Success", f"PDF created successfully: {os.path.basename(output_file)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PngToPdfConverter(root)
    root.mainloop()