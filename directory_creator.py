# modern_directory_creator.py
import os
import sys
import sqlite3
import platform
import csv
import subprocess
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import (
    Qt, QObject, pyqtSignal, QThread, QPropertyAnimation, QEasingCurve, QSize
)
from PyQt5.QtGui import QFont, QIcon, QCursor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox, QCheckBox,
    QFrame, QSpacerItem, QSizePolicy, QGridLayout
)
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

# ---------- Worker to run creation in background ----------
class CreatorWorker(QObject):
    progress = pyqtSignal(int)
    log = pyqtSignal(str, str)  # message, directory/file name
    finished = pyqtSignal(bool, str)  # success, message

    def __init__(self, base_path: str, structure: dict, extras: dict):
        super().__init__()
        self.base_path = base_path
        self.structure = structure
        self.extras = extras
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            total = self._count_tasks(self.structure)
            # extras add a few tasks
            extras_count = 0
            if self.extras.get("readme"): extras_count += 1
            if self.extras.get("gitignore"): extras_count += 1
            if self.extras.get("init_git"): extras_count += 1
            if self.extras.get("venv"): extras_count += 1
            if self.extras.get("open_after"): extras_count += 0
            total += extras_count
            if total == 0:
                self.log.emit("Nothing to create.", "")
                self.finished.emit(True, "Nothing to create")
                return

            tasks_done = 0

            def emit_progress():
                pct = int((tasks_done / total) * 100)
                self.progress.emit(pct)

            # create base project dir
            os.makedirs(self.base_path, exist_ok=True)
            self.log.emit(f"Project folder prepared: {self.base_path}", self.base_path)
            tasks_done += 1
            emit_progress()

            # recursive create
            for root, dirs, files in self._iter_structure(self.base_path, self.structure):
                if self._is_cancelled:
                    self.finished.emit(False, "Cancelled by user")
                    return
                # create directories
                for d in dirs:
                    path_d = os.path.join(root, d)
                    os.makedirs(path_d, exist_ok=True)
                    tasks_done += 1
                    self.log.emit(f"Created directory: {path_d}", d)
                    emit_progress()
                # create files
                for f in files:
                    path_f = os.path.join(root, f)
                    # ensure parent exists
                    os.makedirs(os.path.dirname(path_f), exist_ok=True)
                    if not os.path.exists(path_f):
                        with open(path_f, "w", encoding="utf-8") as fh:
                            # small default content for php/html/readme
                            if f.lower().endswith(".php"):
                                fh.write("<?php\n// auto-generated\n?>\n")
                            elif f.lower().endswith(".md"):
                                fh.write(f"# {os.path.basename(self.base_path)}\n")
                        self.log.emit(f"Created file: {path_f}", f)
                    else:
                        self.log.emit(f"File exists (skipped): {path_f}", f)
                    tasks_done += 1
                    emit_progress()

            # extras
            if self.extras.get("readme"):
                path = os.path.join(self.base_path, "README.md")
                if not os.path.exists(path):
                    with open(path, "w", encoding="utf-8") as fh:
                        fh.write(f"# {os.path.basename(self.base_path)}\n\nGenerated on {datetime.now().isoformat()}\n")
                self.log.emit(f"Created: {path}", "README.md")
                tasks_done += 1
                emit_progress()
            if self.extras.get("gitignore"):
                path = os.path.join(self.base_path, ".gitignore")
                if not os.path.exists(path):
                    with open(path, "w", encoding="utf-8") as fh:
                        fh.write("venv/\n__pycache__/\n*.pyc\n.DS_Store\n")
                self.log.emit(f"Created: {path}", ".gitignore")
                tasks_done += 1
                emit_progress()
            if self.extras.get("venv"):
                venv_path = os.path.join(self.base_path, "venv")
                # create folder as minimal venv placeholder (not a real venv); real venv creation would call venv library
                os.makedirs(venv_path, exist_ok=True)
                self.log.emit(f"Created placeholder venv folder: {venv_path}", "venv")
                tasks_done += 1
                emit_progress()
            if self.extras.get("init_git"):
                # attempt to init git if git exists
                try:
                    subprocess.run(["git", "init", self.base_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.log.emit("Initialized git repository.", "git init")
                except Exception as e:
                    self.log.emit(f"Git init failed or not available: {e}", "git init")
                tasks_done += 1
                emit_progress()

            self.progress.emit(100)
            self.finished.emit(True, "Creation finished successfully")
        except Exception as exc:
            self.finished.emit(False, f"Failed: {exc}")

    def _count_tasks(self, structure):
        total = 0
        for key, val in structure.items():
            # every directory counted as a task to create (except root placeholder if None)
            total += 1
            if isinstance(val, dict):
                total += self._count_tasks(val)
            elif isinstance(val, (list, set, tuple)):
                total += len(val)
            elif val is None:
                total += 1
        return total

    def _iter_structure(self, base_path, structure):
        """
        Yields tuples (root_path, [dirs], [files]) similar to os.walk but based
        on our nested structure dict.
        """
        # We'll build worklist of (root_path, structure_dict)
        stack = [(base_path, structure)]
        while stack:
            root, struct = stack.pop(0)
            dirs = []
            files = []
            for name, content in struct.items():
                if isinstance(content, dict):
                    dirs.append(name)
                elif isinstance(content, (list, set, tuple)):
                    # list/iterable -> create directory 'name' then files inside
                    dirs.append(name)
                elif content is None:
                    # file at this level
                    files.append(name)
            yield root, dirs, files
            # push deeper directories
            for name, content in struct.items():
                if isinstance(content, dict):
                    stack.append((os.path.join(root, name), content))
                elif isinstance(content, (list, set, tuple)):
                    # create the directory, and inside it create listed files
                    inner_files = list(content)
                    # we simulate a structure where that directory contains those files:
                    # yield that directory with no further subdirs but with those files
                    yield os.path.join(root, name), [], inner_files
                # None handled above by files

# ---------- UI helper widgets ----------
class HoverButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._shadow = QGraphicsDropShadowEffect(blurRadius=18, xOffset=0, yOffset=6)
        self._shadow.setColor(Qt.black)
        self.setGraphicsEffect(self._shadow)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self._anim = QPropertyAnimation(self._shadow, b"yOffset")
        # Note: QGraphicsDropShadowEffect doesn't have direct property access to animate in Qt5,
        # but we'll emulate a small "press" effect by changing offset on enter/leave via stylesheet +
        self.setStyleSheet(self.default_style())

    def enterEvent(self, event):
        self.setStyleSheet(self.hover_style())
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.default_style())
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.setStyleSheet(self.pressed_style())
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setStyleSheet(self.hover_style())
        super().mouseReleaseEvent(event)

    def default_style(self):
        return """
            QPushButton {
                border-radius: 10px;
                padding: 10px 14px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                             stop:0 #3a3a3a, stop:1 #2b2b2b);
                color: #fff;
                border: 1px solid rgba(255,255,255,0.04);
            }
        """

    def hover_style(self):
        return """
            QPushButton {
                border-radius: 10px;
                padding: 10px 14px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                             stop:0 #4b8cff, stop:1 #2367d8);
                color: #fff;
                transform: translateY(-2px);
            }
        """

    def pressed_style(self):
        return """
            QPushButton {
                border-radius: 10px;
                padding: 10px 14px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                             stop:0 #1f5fbf, stop:1 #184a9a);
                color: #fff;
                transform: translateY(1px);
            }
        """

# ---------- Main Application ----------
class ModernDirectoryCreator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Project Directory Creator")
        self.setGeometry(150, 100, 1000, 720)
        self.setWindowIcon(QIcon())  # Optionally set an icon file path

        # DB for logs (small)
        self.db_connection = sqlite3.connect("directory_logs_modern.db")
        self._create_logs_table()

        self.user_system_name = platform.node()
        self.selected_directory = None

        # Build UI
        self._setup_ui()
        self._apply_styles()

        # Threading placeholders
        self.worker_thread = None
        self.worker = None

    def _create_logs_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            directory TEXT,
                            user TEXT,
                            timestamp TEXT,
                            path TEXT)''')
        self.db_connection.commit()

    def _setup_ui(self):
        # Top row: Project name + template selector + directory selector
        title = QLabel("Project Directory Creator")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #e6eef8;")

        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Enter project name (e.g. my-app)")
        self.project_name_input.setMinimumWidth(260)

        self.template_combo = QComboBox()
        self.template_combo.addItem("Default Website Template")
        self.template_combo.addItem("Microservice / API Template")  # example placeholders
        self.template_combo.setToolTip("Choose a template layout to pre-populate folders/files")

        self.dir_select_button = HoverButton("Select Parent Directory")
        self.dir_select_button.clicked.connect(self.select_directory)
        self.selected_dir_label = QLabel("No directory selected")
        self.selected_dir_label.setStyleSheet("color: #9aa8b2;")

        # Options
        self.chk_readme = QCheckBox("Create README.md")
        self.chk_gitignore = QCheckBox("Create .gitignore")
        self.chk_init_git = QCheckBox("Init git repo (git must be installed)")
        self.chk_venv = QCheckBox("Create placeholder venv folder")
        self.chk_open_after = QCheckBox("Open folder after creation")
        # default options
        self.chk_readme.setChecked(True)
        self.chk_gitignore.setChecked(True)

        # Create button and progress bar
        self.create_button = HoverButton("Create Structure")
        self.create_button.setFixedHeight(44)
        self.create_button.clicked.connect(self.on_create_clicked)

        self.cancel_button = HoverButton("Cancel")
        self.cancel_button.setFixedHeight(44)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.cancel_button.setEnabled(False)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setTextVisible(False)

        # Logs area and controls
        self.logs_area = QTextEdit()
        self.logs_area.setReadOnly(True)
        self.logs_area.setMinimumHeight(360)
        self.logs_area.setStyleSheet("background: #0f1417; color: #9fffb0;")

        self.export_logs_btn = HoverButton("Export Logs (CSV)")
        self.export_logs_btn.clicked.connect(self.export_logs)

        self.show_db_logs_btn = HoverButton("Show DB Logs")
        self.show_db_logs_btn.clicked.connect(self.show_db_logs_dialog)

        # Layout assembly
        main_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.addWidget(QLabel("Project Name:"), 0, 0, alignment=Qt.AlignRight)
        grid.addWidget(self.project_name_input, 0, 1)
        grid.addWidget(QLabel("Template:"), 0, 2, alignment=Qt.AlignRight)
        grid.addWidget(self.template_combo, 0, 3)

        grid.addWidget(self.dir_select_button, 1, 0)
        grid.addWidget(self.selected_dir_label, 1, 1, 1, 3)

        # options area as a card-like frame
        card = QFrame()
        card_layout = QHBoxLayout()
        card_layout.addWidget(self.chk_readme)
        card_layout.addWidget(self.chk_gitignore)
        card_layout.addWidget(self.chk_init_git)
        card_layout.addWidget(self.chk_venv)
        card_layout.addWidget(self.chk_open_after)
        card.setLayout(card_layout)
        card.setFrameShape(QFrame.StyledPanel)
        card.setObjectName("optionsCard")

        main_layout.addLayout(grid)
        main_layout.addWidget(card)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.create_button)
        btn_row.addWidget(self.cancel_button)
        btn_row.addStretch()
        btn_row.addWidget(self.export_logs_btn)
        btn_row.addWidget(self.show_db_logs_btn)
        main_layout.addLayout(btn_row)

        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(QLabel("Activity Log:"))
        main_layout.addWidget(self.logs_area)

        self.setLayout(main_layout)

    def _apply_styles(self):
        # overall window style
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #0b0f12, stop:1 #0f1417);
                color: #dbe9f5;
                font-family: "Segoe UI", Arial;
            }
            QLineEdit, QComboBox {
                background: #161a1d;
                border: 1px solid rgba(255,255,255,0.04);
                padding: 8px;
                border-radius: 8px;
                color: #ecf3ff;
            }
            QTextEdit {
                border: 1px solid rgba(255,255,255,0.04);
                border-radius: 8px;
                padding: 10px;
            }
            QCheckBox {
                color: #bcd7ff;
            }
            #optionsCard {
                background: rgba(255,255,255,0.02);
                border-radius: 12px;
                padding: 8px;
            }
            QProgressBar {
                border-radius: 9px;
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.03);
            }
            QProgressBar::chunk {
                border-radius: 9px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6ad1ff, stop:1 #2b8cff);
            }
        """)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Parent Directory", os.path.expanduser("~"))
        if directory:
            self.selected_directory = directory
            self.selected_dir_label.setText(directory)
            self.append_log(f"Selected parent directory: {directory}", directory)
            self.reset_progress_bar()
        else:
            self.selected_dir_label.setText("No directory selected")

    def on_create_clicked(self):
        project_name = self.project_name_input.text().strip()
        if not project_name:
            QMessageBox.warning(self, "Input Error", "Please enter a project name.")
            return
        if not self.selected_directory:
            QMessageBox.warning(self, "Input Error", "Please select a parent directory.")
            return

        project_path = os.path.join(self.selected_directory, project_name)
        if os.path.exists(project_path):
            resp = QMessageBox.question(self, "Already exists", f"Project path already exists:\n{project_path}\nOverwrite / add into it?")
            # if user cancels, stop
            if resp == QMessageBox.Cancel:
                return

        # choose template -> map to structure
        template_name = self.template_combo.currentText()
        structure = self._get_template_structure(template_name)

        extras = {
            "readme": self.chk_readme.isChecked(),
            "gitignore": self.chk_gitignore.isChecked(),
            "init_git": self.chk_init_git.isChecked(),
            "venv": self.chk_venv.isChecked(),
            "open_after": self.chk_open_after.isChecked(),
        }

        # disable/enable buttons
        self.create_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        # start worker thread
        self.worker = CreatorWorker(project_path, structure, extras)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_progress)
        self.worker.log.connect(self.append_log)
        self.worker.finished.connect(self.on_finished)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

        self.append_log(f"Started creation for: {project_path}", project_name)

    def on_cancel_clicked(self):
        if self.worker:
            self.worker.cancel()
            self.append_log("Cancellation requested. Waiting for worker to stop...", "")
            self.cancel_button.setEnabled(False)

    def on_progress(self, val: int):
        self.progress_bar.setValue(val)

    def on_finished(self, success: bool, message: str):
        self.append_log(message, "")
        self.create_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(100 if success else 0)
        # write final log to DB
        if self.selected_directory:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor = self.db_connection.cursor()
            cursor.execute('INSERT INTO logs (directory, user, timestamp, path) VALUES (?, ?, ?, ?)',
                           (self.project_name_input.text().strip(), self.user_system_name, timestamp, self.selected_directory))
            self.db_connection.commit()

        # Open folder if user requested and successful
        if success and self.chk_open_after.isChecked():
            try:
                path_to_open = os.path.join(self.selected_directory, self.project_name_input.text().strip())
                if sys.platform == "win32":
                    os.startfile(path_to_open)
                elif sys.platform == "darwin":
                    subprocess.run(["open", path_to_open])
                else:
                    subprocess.run(["xdg-open", path_to_open])
            except Exception as e:
                self.append_log(f"Failed to open folder: {e}", "")

        QMessageBox.information(self, "Finished", message)

    def append_log(self, message: str, name: str):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logs_area.append(f"[{ts}] {message}")
        # Also insert compact log into DB if name provided
        if name:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('INSERT INTO logs (directory, user, timestamp, path) VALUES (?, ?, ?, ?)',
                               (name, self.user_system_name, ts, self.selected_directory or ""))
                self.db_connection.commit()
            except Exception:
                pass

    def export_logs(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Logs CSV", os.path.expanduser("~/dir_creator_logs.csv"), "CSV Files (*.csv)")
        if not path:
            return
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id, directory, user, timestamp, path FROM logs")
            rows = cursor.fetchall()
            with open(path, "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(["id", "directory", "user", "timestamp", "path"])
                writer.writerows(rows)
            QMessageBox.information(self, "Exported", f"Logs exported to {path}")
        except Exception as e:
            QMessageBox.warning(self, "Export failed", str(e))

    def show_db_logs_dialog(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT id, directory, user, timestamp, path FROM logs ORDER BY id DESC LIMIT 200")
        rows = cursor.fetchall()
        text = "\n".join([f"ID:{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}" for r in rows]) or "(no logs)"
        QMessageBox.information(self, "Recent logs", text)

    def reset_progress_bar(self):
        self.progress_bar.setValue(0)

    def closeEvent(self, event):
        try:
            self.db_connection.close()
        except Exception:
            pass
        event.accept()

    def _get_template_structure(self, template_name: str):
        # A more complete / nested structure mapping - feel free to extend templates
        default = {
            'Assets': {
                'Accounts': {
                    'Contents': {},
                    'Pages': ['login.php', 'register.php', 'user-dashboard.php'],
                    'Processors': ['login-endpoint.php', 'register-endpoint.php', 'userinfo-endpoint.php', 'logout-endpoint.php'],
                    'Scripts': ['accounts.js'],
                    'Styles': {},
                },
                'Admins': {
                    'Contents': ['admin-login-page.php','admin-cards.php','admin-analytics.php'],
                    'Pages': ['admin-dashboard.php','admin-access.php','admin-logout.php'],
                    'Processors': ['admin-access-endpoint.php','admin-logout-endpoint.php'],
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
        microservice = {
            'src': {
                'controllers': {},
                'models': {},
                'routes': ['api.py'],
                'utils': {},
            },
            'tests': {},
            'docs': {},
            'Dockerfile': None,
            'requirements.txt': None,
            'main.py': None,
        }
        if "micro" in template_name.lower():
            return microservice
        return default

# ---------- Run ----------
def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    w = ModernDirectoryCreator()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
