import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re

class FileSequenceChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("File Sequence Checker")
        self.root.geometry("500x300")
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Title label
        title_label = tk.Label(self.root, text="File Sequence Checker", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Instructions
        instruction_label = tk.Label(self.root, 
                                   text="Select a folder to check file sequence",
                                   font=("Arial", 10))
        instruction_label.pack(pady=5)
        
        # Select folder button
        select_button = tk.Button(self.root, text="Select Folder", 
                                 command=self.select_folder,
                                 font=("Arial", 12),
                                 bg="#4CAF50", fg="white",
                                 padx=20, pady=10)
        select_button.pack(pady=20)
        
        # Results text area
        self.result_text = tk.Text(self.root, width=60, height=12,
                                  font=("Arial", 11))
        self.result_text.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Scrollbar for text area
        scrollbar = tk.Scrollbar(self.result_text)
        scrollbar.pack(side="right", fill="y")
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)
        
    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            self.analyze_files(folder_path)
    
    def analyze_files(self, folder_path):
        try:
            # Clear previous results
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Folder: {os.path.basename(folder_path)}\n")
            self.result_text.insert(tk.END, "="*40 + "\n\n")
            
            # Array 1: All file names
            all_files = []
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    all_files.append(item)
            
            if not all_files:
                self.result_text.insert(tk.END, "❌ No files found in the selected folder.\n")
                return
            
            # Array 2: File names without extensions
            files_without_ext = []
            for filename in all_files:
                name_without_ext = os.path.splitext(filename)[0]
                files_without_ext.append(name_without_ext)
            
            # Array 3: Last 4 digits from each filename
            last_four_digits = []
            invalid_files = []
            
            for i, filename in enumerate(files_without_ext):
                match = re.search(r'(\d{4})$', filename)
                if match:
                    last_four_digits.append(int(match.group(1)))
                else:
                    # Try to find any digits at the end
                    match = re.search(r'(\d+)$', filename)
                    if match:
                        digits = match.group(1)
                        if len(digits) >= 4:
                            last_four_digits.append(int(digits[-4:]))
                        else:
                            invalid_files.append((all_files[i], f"Only {len(digits)} digits"))
                    else:
                        invalid_files.append((all_files[i], "No digits at end"))
            
            # Print total size
            self.result_text.insert(tk.END, f"Total files processed: {len(last_four_digits)}\n\n")
            
            # Show files that couldn't be processed
            if invalid_files:
                self.result_text.insert(tk.END, "⚠️  Files that couldn't be processed:\n")
                for filename, reason in invalid_files:
                    self.result_text.insert(tk.END, f"   • {filename} - {reason}\n")
                self.result_text.insert(tk.END, "\n")
            
            if len(last_four_digits) == 0:
                self.result_text.insert(tk.END, "❌ No valid files with 4-digit endings found.\n")
                return
            
            # Check arithmetic progression
            self.check_arithmetic_progression(last_four_digits)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def check_arithmetic_progression(self, numbers):
        if len(numbers) <= 1:
            self.result_text.insert(tk.END, "⚠️  Not enough numbers to check sequence.\n")
            return
        
        # Sort the numbers to check sequence properly
        sorted_numbers = sorted(numbers)
        
        # Check for duplicates
        duplicates = []
        seen = set()
        for num in sorted_numbers:
            if num in seen:
                if num not in [d[1] for d in duplicates]:  # Avoid duplicate reporting
                    duplicates.append(("Duplicate", num))
            seen.add(num)
        
        # Check for arithmetic progression with difference of 1
        missing_numbers = []
        expected = sorted_numbers[0]
        
        for current in sorted_numbers:
            while expected < current:
                missing_numbers.append(expected)
                expected += 1
            expected = current + 1
        
        # Report results
        if missing_numbers or duplicates:
            self.result_text.insert(tk.END, "❌ SEQUENCE ISSUES FOUND:\n")
            self.result_text.insert(tk.END, "="*25 + "\n")
            
            if duplicates:
                self.result_text.insert(tk.END, "Duplicate numbers:\n")
                unique_duplicates = list(set([num for _, num in duplicates]))
                for number in unique_duplicates:
                    self.result_text.insert(tk.END, f"   • {number:04d}\n")
                self.result_text.insert(tk.END, "\n")
            
            if missing_numbers:
                self.result_text.insert(tk.END, "Missing numbers in sequence:\n")
                for number in missing_numbers:
                    self.result_text.insert(tk.END, f"   • {number:04d}\n")
                self.result_text.insert(tk.END, "\n")
            
        else:
            self.result_text.insert(tk.END, "✅ VERIFICATION SUCCESSFUL!\n")
            self.result_text.insert(tk.END, "="*25 + "\n")
            self.result_text.insert(tk.END, "Perfect arithmetic progression with increment of 1.\n")
            self.result_text.insert(tk.END, f"Sequence: {sorted_numbers[0]:04d} to {sorted_numbers[-1]:04d}\n")

def main():
    root = tk.Tk()
    app = FileSequenceChecker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
