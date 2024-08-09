import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QApplication, QMessageBox

class DirectoryCreator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set the main window properties
        self.setWindowTitle('Project Directory Creator')
        self.setGeometry(100, 100, 800, 600)  # Set a specific size for the window
        self.setStyleSheet("background-color: #121212; color: white;")

        # Project name input
        self.project_name_label = QtWidgets.QLabel('Enter Project Name:', self)
        self.project_name_label.setGeometry(QtCore.QRect(50, 50, 200, 30))
        self.project_name_input = QtWidgets.QLineEdit(self)
        self.project_name_input.setGeometry(QtCore.QRect(260, 50, 400, 30))
        self.project_name_input.setStyleSheet("background-color: #333; color: white; border: 1px solid #555;")

        # Directory selection button and label
        self.dir_select_button = QtWidgets.QPushButton('Select Directory', self)
        self.dir_select_button.setGeometry(QtCore.QRect(50, 100, 150, 30))
        self.dir_select_button.setStyleSheet("background-color: #444; color: white; border: 1px solid #555;")
        self.dir_select_button.clicked.connect(self.select_directory)

        self.selected_dir_label = QtWidgets.QLabel('No directory selected', self)
        self.selected_dir_label.setGeometry(QtCore.QRect(210, 100, 550, 30))
        self.selected_dir_label.setStyleSheet("color: #aaa;")

        # Create structure button
        self.create_button = QtWidgets.QPushButton('Create Structure', self)
        self.create_button.setGeometry(QtCore.QRect(50, 150, 150, 30))
        self.create_button.setStyleSheet("background-color: #5cb85c; color: white; border: 1px solid #555;")
        self.create_button.clicked.connect(self.create_structure)

        # Logs area
        self.logs_label = QtWidgets.QLabel('Logs:', self)
        self.logs_label.setGeometry(QtCore.QRect(50, 200, 100, 30))
        self.logs_area = QtWidgets.QTextEdit(self)
        self.logs_area.setGeometry(QtCore.QRect(50, 230, 700, 300))
        self.logs_area.setStyleSheet("background-color: #222; color: green; border: 1px solid #555;")
        self.logs_area.setReadOnly(True)

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setGeometry(QtCore.QRect(50, 550, 700, 30))
        self.progress_bar.setStyleSheet("QProgressBar::chunk {background-color: #5cb85c;}")

        self.selected_directory = None

    def select_directory(self):
        self.selected_directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.selected_dir_label.setText(self.selected_directory if self.selected_directory else "No directory selected")

    def create_structure(self):
        project_name = self.project_name_input.text()
        if not project_name:
            QMessageBox.warning(self, "Input Error", "Please enter a project directory name.")
            return
        if not self.selected_directory:
            QMessageBox.warning(self, "Input Error", "Please select a directory.")
            return

        project_path = os.path.join(self.selected_directory, project_name)

        # Define the structure
        structure = {
            'Assets': {
                'Accounts': {
                    'Contents': [],
                    'Pages': ['login.php', 'register.php', 'user-dashboard.php'],
                    'Processors': [],
                    'Scripts': ['accounts.js'],
                    'Styles': [],
                },
                'Admins': {
                    'Contents': [],
                    'Pages': ['admin-dashboard.php'],
                    'Processors': [],
                    'Scripts': [],
                    'Styles': [],
                },
                'Connections': [],
                'Extras': {
                    'Documentations': [],
                    'Helps': [],
                    'Updates': [],
                },
                'Website': {
                    'Contents': [],
                    'Images': [],
                    'Pages': ['about-us.php', 'contact.php', 'faqs.php', 'privacy-policy.php', 'terms-conditions.php'],
                    'Processors': [],
                    'Scripts': ['main.js'],
                    'Styles': [],
                    'Videos': [],
                },
            },
            'index.php': [],
        }

        total_tasks = self.count_tasks(structure)
        tasks_completed = 0

        def create_folders(path, structure):
            nonlocal tasks_completed
            try:
                for item, content in structure.items():
                    current_path = os.path.join(path, item)
                    if isinstance(content, dict):
                        if not os.path.exists(current_path):
                            os.makedirs(current_path)
                            self.logs_area.append(f"Created directory: {current_path}")
                        create_folders(current_path, content)
                    else:
                        # Create an empty directory if it's not a dict
                        if not os.path.exists(current_path):
                            os.makedirs(current_path)
                            self.logs_area.append(f"Created directory: {current_path}")
                    tasks_completed += 1
                    self.progress_bar.setValue((tasks_completed / total_tasks) * 100)
            except Exception as e:
                self.logs_area.append(f"Error creating directory {path}: {str(e)}")

        def create_files(path, structure):
            nonlocal tasks_completed
            try:
                for item, content in structure.items():
                    current_path = os.path.join(path, item)
                    if isinstance(content, dict):
                        create_files(current_path, content)
                    elif isinstance(content, list):
                        for file in content:
                            file_path = os.path.join(path, file)
                            if not os.path.exists(file_path):
                                with open(file_path, 'w') as f:
                                    pass
                                self.logs_area.append(f"Created file: {file_path}")
                            tasks_completed += 1
                            self.progress_bar.setValue((tasks_completed / total_tasks) * 100)
            except Exception as e:
                self.logs_area.append(f"Error creating file in {path}: {str(e)}")

        # Create folders first
        create_folders(project_path, structure)

        # Create files next
        create_files(project_path, structure)

        self.logs_area.append("Directory structure created successfully.")
        self.progress_bar.setValue(100)

    def count_tasks(self, structure):
        total = 0
        for item in structure.values():
            if isinstance(item, dict):
                total += self.count_tasks(item)
            else:
                total += len(item)
        return total

# Main function to run the application
def main():
    app = QApplication(sys.argv)
    ex = DirectoryCreator()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
