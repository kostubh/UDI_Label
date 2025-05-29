import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pylibdmtx.pylibdmtx import encode, decode
from PIL import Image
import threading
import time

class DataMatrixGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("DataMatrix Generator")
        self.root.geometry("600x450")
        self.root.configure(bg="#f0f0f0")
        
        self.is_processing = False
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="DataMatrix Generator", font=("Arial", 16, "bold"), bg="#f0f0f0")
        title_label.pack(pady=(0, 20))
        
        # Input fields frame
        input_frame = tk.Frame(main_frame, bg="#f0f0f0")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Base data input
        base_data_label = tk.Label(input_frame, text="Base Data:", bg="#f0f0f0", font=("Arial", 10, "bold"))
        base_data_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.base_data = tk.Text(input_frame, height=4, width=50, font=("Arial", 10))
        self.base_data.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.base_data.insert("1.0", """(01)843041125857
(11)250602
(10)LTTI0625
(21)2506ZLD60XSW""")
        
        # Range inputs
        range_frame = tk.Frame(input_frame, bg="#f0f0f0")
        range_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        start_label = tk.Label(range_frame, text="Start Number:", bg="#f0f0f0", font=("Arial", 10))
        start_label.grid(row=0, column=0, padx=(0, 5), sticky="w")
        
        self.start_number = tk.Entry(range_frame, width=8, font=("Arial", 10))
        self.start_number.grid(row=0, column=1, padx=(0, 15))
        self.start_number.insert(0, "1")
        
        end_label = tk.Label(range_frame, text="End Number:", bg="#f0f0f0", font=("Arial", 10))
        end_label.grid(row=0, column=2, padx=(0, 5), sticky="w")
        
        self.end_number = tk.Entry(range_frame, width=8, font=("Arial", 10))
        self.end_number.grid(row=0, column=3)
        self.end_number.insert(0, "3000")
        
        # Output folder selection
        folder_frame = tk.Frame(main_frame, bg="#f0f0f0")
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.output_folder = tk.StringVar(value="Data_MatrixImages")
        folder_label = tk.Label(folder_frame, text="Output Folder:", bg="#f0f0f0", font=("Arial", 10, "bold"))
        folder_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        folder_entry = tk.Entry(folder_frame, textvariable=self.output_folder, width=40, font=("Arial", 10))
        folder_entry.grid(row=1, column=0, padx=(0, 10), sticky="ew")
        
        browse_button = tk.Button(folder_frame, text="Browse", command=self.browse_folder, 
                                font=("Arial", 10), bg="#4CAF50", fg="white", padx=10)
        browse_button.grid(row=1, column=1)
        
        # Add checkbox for Data_MatrixImages subfolder
        self.use_subfolder = tk.BooleanVar(value=True)  # Default to True
        subfolder_check = tk.Checkbutton(folder_frame, 
                                       text="Create 'Data_MatrixImages' subfolder",
                                       variable=self.use_subfolder,
                                       bg="#f0f0f0",
                                       font=("Arial", 10))
        subfolder_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Progress frame
        self.progress_frame = tk.Frame(main_frame, bg="#f0f0f0")
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_label = tk.Label(self.progress_frame, text="", bg="#f0f0f0", font=("Arial", 10))
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate', length=400)
        self.progress_bar.pack(pady=(5, 0))
        
        self.progress_frame.pack_forget()  # Hide initially
        
        # Generate button
        self.generate_button = tk.Button(main_frame, text="Generate DataMatrix Images", 
                                       command=self.start_generation,
                                       font=("Arial", 12), bg="#2196F3", fg="white", padx=10, pady=5)
        self.generate_button.pack(pady=(10, 0))
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
    
    def get_output_path(self):
        base_path = self.output_folder.get()
        if self.use_subfolder.get():
            return os.path.join(base_path, "Data_MatrixImages")
        return base_path
    
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
        
        try:
            start = int(self.start_number.get())
            end = int(self.end_number.get())
            
            if start < 1 or end < start:
                messagebox.showerror("Error", "Please enter valid start and end numbers")
                return
            
            base_data = self.base_data.get("1.0", tk.END).strip()
            if not base_data:
                messagebox.showerror("Error", "Please enter base data")
                return
            
            output_folder = self.get_output_path()
            if not output_folder:
                messagebox.showerror("Error", "Please select an output folder")
                return
            
            # Create the folder if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)
            
            # Start generation in separate thread
            self.is_processing = True
            self.generate_button.config(state=tk.DISABLED, text="Generating...")
            
            threading.Thread(target=self.generate_datamatrix, 
                           args=(base_data, start, end, output_folder), 
                           daemon=True).start()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for start and end")
            self.is_processing = False
            self.generate_button.config(state=tk.NORMAL, text="Generate DataMatrix Images")
    
    def generate_datamatrix(self, base_data, start, end, output_folder):
        try:
            total = end - start + 1
            self.root.after(0, lambda: self.show_progress("Starting generation...", 0, total))
            
            # Extract the value of field (21) from the base data
            field_21_value = base_data.split('(21)')[-1].strip()
            
            for i in range(start, end + 1):
                # Update progress
                self.root.after(0, lambda curr=i-start+1: self.update_progress(curr, total))
                
                # Update the changing part to be a four-digit number
                data = base_data + f'{i:04d}'
                
                # Encode the data
                encoded = encode(data.encode('utf8'))
                
                # Create an image from the encoded data
                img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
                
                new_size = (encoded.width * 4, encoded.height * 4)  # Scale by 4x
                img = img.resize(new_size, Image.Resampling.NEAREST)  # Nearest neighbor for barcodes
                
                # Save the image
                img_path = os.path.join(output_folder, f'{field_21_value}{i:04d}.png')
                img.save(img_path, dpi=(600, 600))
                
                # Small delay to prevent overwhelming the system
                if i % 10 == 0:
                    time.sleep(0.01)
            
            # Success message
            self.root.after(0, lambda: self.generation_complete(output_folder))
            
        except Exception as e:
            self.root.after(0, lambda: self.handle_error(f"An error occurred: {str(e)}"))
    
    def generation_complete(self, output_folder):
        self.hide_progress()
        self.is_processing = False
        self.generate_button.config(state=tk.NORMAL, text="Generate DataMatrix Images")
        messagebox.showinfo("Success", f"DataMatrix images created successfully!\nOutput folder: {output_folder}")
    
    def handle_error(self, error_message):
        self.hide_progress()
        self.is_processing = False
        self.generate_button.config(state=tk.NORMAL, text="Generate DataMatrix Images")
        messagebox.showerror("Error", error_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = DataMatrixGenerator(root)
    root.mainloop()
