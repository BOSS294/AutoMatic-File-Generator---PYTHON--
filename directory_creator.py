import os
import customtkinter as ctk
from tkinter import filedialog, messagebox, Tk

class DirectoryCreator(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Project Directory Creator")
        self.geometry("800x600")
        self.configure(fg_color="#121212")

        # Project name input
        self.project_name_label = ctk.CTkLabel(self, text="Enter Project Name:", text_color="Red") # Added Red Color to make it more attractive
        self.project_name_label.place(x=50, y=50)
        self.project_name_input = ctk.CTkEntry(self, width=400, fg_color="#333", text_color="white", border_color="#555")
        self.project_name_input.place(x=260, y=50)

        # Directory selection button and label
        self.dir_select_button = ctk.CTkButton(self, text="Select Directory", command=self.select_directory, fg_color="#444", text_color="white", hover_color="#5cb85c") # Added green Color on selection to make it more attractive
        self.dir_select_button.place(x=50, y=100)
        self.selected_dir_label = ctk.CTkLabel(self, text="No directory selected", text_color="#aaa")
        self.selected_dir_label.place(x=210, y=100)

        

        # Create structure button
        self.create_button = ctk.CTkButton(self, text="Create Structure", command=self.create_structure, fg_color="#5cb85c", text_color="white", hover_color="#4cae4c")
        self.create_button.place(x=50, y=150)

        # Logs area
        self.logs_label = ctk.CTkLabel(self, text="Logs:", text_color="white")
        self.logs_label.place(x=50, y=200)
        self.logs_area = ctk.CTkTextbox(self, width=700, height=300, fg_color="#222", text_color="green", border_color="#555")
        self.logs_area.place(x=50, y=230)
        self.logs_area.configure(state="disabled")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self, width=700, fg_color="#d9534f", progress_color="#d9534f", mode="determinate")
        self.progress_bar.place(x=50, y=550)
        self.progress_bar.set(0)

        self.selected_directory = None

    def select_directory(self):
        self.selected_directory = filedialog.askdirectory(title="Select Directory")
        self.selected_dir_label.configure(text=self.selected_directory if self.selected_directory else "No directory selected")
        self.reset_progress_bar()

    def create_structure(self):
        project_name = self.project_name_input.get()
        if not project_name:
            messagebox.showwarning("Input Error", "Please enter a project directory name before proceeding.") # Added English language bit more
            return
        if not self.selected_directory:
            messagebox.showwarning("Input Error", "Please select a directory before proceeding.") # Added English Language Bit more
            return

        project_path = os.path.join(self.selected_directory, project_name)
        
        # Reset progress bar to red
        self.progress_bar.configure(fg_color="#d9534f", progress_color="#d9534f")
        self.progress_bar.set(0)

        # Define the structure
        structure = {
            'Assets': {
                'Accounts': {
                    'Contents': {},
                    'Pages': ['login.php', 'register.php', 'user-dashboard.php'],
                    'Processors': {},
                    'Scripts': ['accounts.js'],
                    'Styles': {},
                },
                'Admins': {
                    'Contents': {},
                    'Pages': ['admin-dashboard.php'],
                    'Processors': {},
                    'Scripts': {},
                    'Styles': {},
                },
                'Extras': {
                    'Connections': {},
                    'Documentations': {},
                    'Helps': {},
                    'Updates': {},
                },
                'Website': {
                    'Contents': {},
                    'Images': {},
                    'Pages': ['about-us.php', 'contact.php', 'faqs.php', 'privacy-policy.php', 'terms-conditions.php'],
                    'Processors': {},
                    'Scripts': ['main.js'],
                    'Styles': {},
                    'Videos': {},
                },
                'Miscellaneous': {
                    'Context': {},
                    'Information': {},
                    'File Dumping': {},
                    'Testing Purpose': {},
                },
            },
            'index.php': None,  # Mark as None to indicate it's a file, not a directory
        }

        total_tasks = self.count_tasks(structure)
        tasks_completed = 0

        def create_folders_and_files(path, structure):
            nonlocal tasks_completed
            try:
                for item, content in structure.items():
                    current_path = os.path.join(path, item)

                    if isinstance(content, dict):
                        # Create the directory if it doesn't exist
                        if not os.path.exists(current_path):
                            os.makedirs(current_path)
                            self.append_log(f"Created directory: {current_path}")
                        # Recursively create subfolders and files
                        create_folders_and_files(current_path, content)
                    elif isinstance(content, list):
                        # Create the directory for this list of files
                        if not os.path.exists(current_path):
                            os.makedirs(current_path)
                            self.append_log(f"Created directory: {current_path}")
                        for file in content:
                            file_path = os.path.join(current_path, file)
                            if not os.path.exists(file_path):
                                with open(file_path, 'w') as f:
                                    pass  # Create an empty file
                                self.append_log(f"Created file: {file_path}")
                    elif content is None:  # Handle files like index.php
                        if not os.path.exists(current_path):
                            with open(current_path, 'w') as f:
                                pass  # Create an empty file
                            self.append_log(f"Created file: {current_path}")

                    tasks_completed += 1
                    self.progress_bar.set(tasks_completed / total_tasks)
            except Exception as e:
                self.append_log(f"Error creating directory or file in {path}: {str(e)}")

        # Create folders and files
        create_folders_and_files(project_path, structure)


        self.append_log("\n\n\nDirectory structure has been created successfully\n\n\n") #English Improvement & Highlighted
        
        # Turn the progress bar green on successful completion
        self.progress_bar.configure(fg_color="#5cb85c", progress_color="#5cb85c")
        self.progress_bar.set(1)

    def count_tasks(self, structure):
        total = 0
        for item in structure.values():
            if isinstance(item, dict):
                total += self.count_tasks(item)
            elif isinstance(item, list):
                total += len(item)
            elif item is None:  # Handle the case where it's a single file like 'index.php'
                total += 1
        return total

    def append_log(self, message):
        self.logs_area.configure(state="normal")
        self.logs_area.insert(ctk.END, message + "\n")
        self.logs_area.configure(state="disabled")
        self.logs_area.yview(ctk.END)

    def reset_progress_bar(self):
        # Reset the progress bar to red when selecting a new directory
        self.progress_bar.configure(fg_color="#d9534f", progress_color="#d9534f")
        self.progress_bar.set(0)

# Main function to run the application
if __name__ == "__main__":
    app = ctk.CTk()
    creator = DirectoryCreator()
    creator.mainloop()
