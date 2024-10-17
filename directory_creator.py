import os
import sqlite3
import platform
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox, Tk

class DirectoryCreator(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Project Directory Creator")
        self.geometry("800x600")
        self.configure(fg_color="#121212")

        # Initialize SQLite database
        self.db_connection = sqlite3.connect("directory_logs.db")
        self.create_logs_table()

        # Get the system's hostname
        self.user_system_name = platform.node()

        # Project name input
        self.project_name_label = ctk.CTkLabel(self, text="Enter Project Name:", text_color="Red")
        self.project_name_label.place(x=50, y=50)
        self.project_name_input = ctk.CTkEntry(self, width=400, fg_color="#333", text_color="white", border_color="#555")
        self.project_name_input.place(x=260, y=50)

        # Directory selection button and label
        self.dir_select_button = ctk.CTkButton(self, text="Select Directory", command=self.select_directory, fg_color="#444", text_color="white", hover_color="#5cb85c")
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

        # Show Logs button
        self.show_logs_button = ctk.CTkButton(self, text="Show Logs", command=self.show_logs, fg_color="#007bff", text_color="white", hover_color="#0056b3")
        self.show_logs_button.place(x=50, y=500)

        self.selected_directory = None

    def create_logs_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            directory TEXT,
                            user TEXT,
                            timestamp TEXT,
                            path TEXT)''')
        self.db_connection.commit()

    def select_directory(self):
        self.selected_directory = filedialog.askdirectory(title="Select Directory")
        self.selected_dir_label.configure(text=self.selected_directory if self.selected_directory else "No directory selected")
        self.reset_progress_bar()

    def create_structure(self):
        project_name = self.project_name_input.get()
        if not project_name:
            messagebox.showwarning("Input Error", "Please enter a project directory name before proceeding.")
            return
        if not self.selected_directory:
            messagebox.showwarning("Input Error", "Please select a directory before proceeding.")
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
                    'Processors': ['login-endpoint.php','register-endpoint.php','userinfo-endpoint.php','logout-endpoint.php'],
                    'Scripts': ['accounts.js'],
                    'Styles': {},
                },
                'Admins': {
                    'Contents': {'admin-login-page.php','admin-cards.php','admin-analytics.php'},
                    'Pages': ['admin-dashboard.php','admin-access.php','admin-logout.php'],
                    'Processors': ['admin-access-endpoint.php','admin-logout-endpoint.php','admin-logout-endpoint.php'],
                    'Scripts': ['admin-notifications.js'],
                    'Resources': ['anav.php'],
                    'Styles': {},
                },
                'Resources': {
                    'File Dumping': {},

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
            'index.php': None,
        }

        total_tasks = self.count_tasks(structure)
        tasks_completed = 0

        def create_folders_and_files(path, structure):
            nonlocal tasks_completed
            try:
                for item, content in structure.items():
                    current_path = os.path.join(path, item)

                    if isinstance(content, dict):
                        if not os.path.exists(current_path):
                            os.makedirs(current_path)
                            self.append_log(f"Created directory: {current_path}", directory=item)
                        create_folders_and_files(current_path, content)
                    elif isinstance(content, list):
                        if not os.path.exists(current_path):
                            os.makedirs(current_path)
                            self.append_log(f"Created directory: {current_path}", directory=item)
                        for file in content:
                            file_path = os.path.join(current_path, file)
                            if not os.path.exists(file_path):
                                with open(file_path, 'w') as f:
                                    pass  # Create an empty file
                                self.append_log(f"Created file: {file_path}", directory=file)
                    elif content is None:
                        if not os.path.exists(current_path):
                            with open(current_path, 'w') as f:
                                pass  # Create an empty file
                            self.append_log(f"Created file: {current_path}", directory=item)

                    tasks_completed += 1
                    self.progress_bar.set(tasks_completed / total_tasks)
            except Exception as e:
                self.append_log(f"Error creating directory or file in {path}: {str(e)}")

        # Create folders and files
        create_folders_and_files(project_path, structure)

        self.append_log("\n\n\nDirectory structure has been created successfully\n\n\n") 
        
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

    def append_log(self, message, directory=None):
        self.logs_area.configure(state="normal")
        self.logs_area.insert(ctk.END, message + "\n")
        self.logs_area.configure(state="disabled")
        self.logs_area.yview(ctk.END)

        # Insert log into the database
        if directory:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor = self.db_connection.cursor()
            cursor.execute('INSERT INTO logs (directory, user, timestamp, path) VALUES (?, ?, ?, ?)', 
                           (directory, self.user_system_name, timestamp, self.selected_directory))
            self.db_connection.commit()

    def show_logs(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM logs")
        logs = cursor.fetchall()

        log_text = "\n".join([f"ID: {log[0]}, Directory: {log[1]}, User: {log[2]}, Timestamp: {log[3]}, Path: {log[4]}" for log in logs])
        messagebox.showinfo("Logs", log_text)

    def reset_progress_bar(self):
        # Reset the progress bar to red when selecting a new directory
        self.progress_bar.configure(fg_color="#d9534f", progress_color="#d9534f")
        self.progress_bar.set(0)

    def on_closing(self):
        self.db_connection.close()
        self.destroy()

# Main function to run the application
if __name__ == "__main__":
    app = ctk.CTk()
    creator = DirectoryCreator()
    app.protocol("WM_DELETE_WINDOW", creator.on_closing)
    creator.mainloop()
