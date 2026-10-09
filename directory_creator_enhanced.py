# modern_directory_creator_enhanced.py
"""
AutoMatic File Generator - Professional Project Structure Generator with Intelligent Branding
Version: 2.1.0 - Enhanced UI/UX
Author: Mayank Chawdhari (BOSS294)
Organization: Privonix Technologies
"""

import os
import sys
import sqlite3
import platform
import csv
import subprocess
import re
import json
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import (
    Qt, QObject, pyqtSignal, QThread, QPropertyAnimation, QEasingCurve, QSize,
    QTimer, QRect, QPoint, QEvent, QMimeData
)
from PyQt5.QtGui import (
    QFont, QIcon, QCursor, QColor, QPalette, QBrush, QPixmap, QPainter,
    QLinearGradient, QRadialGradient, QPen
)
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox, QCheckBox,
    QFrame, QSpacerItem, QSizePolicy, QGridLayout, QScrollArea, QListWidget,
    QListWidgetItem, QDialog, QTabWidget, QStyledItemDelegate, QSpinBox,
    QDoubleSpinBox, QSlider, QStyle
)
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

# ---------- Project Branding System ----------
class ProjectBranding:
    """
    Generates and manages project-specific branding for Connector layer.

    Pattern Examples:
        "NileAndSinai" -> NSA, nsa_, NileAndSinaiBootstrap, NSA_BOOTSTRAP_VERSION
        "NexPlacify" -> NXP, nxp_, NexPlacifyBootstrap, NXP_BOOTSTRAP_VERSION
        "MyProject" -> MP, mp_, MyProjectBootstrap, MP_BOOTSTRAP_VERSION
    """

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.project_key = self._extract_key(project_name)
        self.project_prefix = self.project_key.lower() + "_"
        self.bootstrap_class = project_name + "Bootstrap"
        self.version_constant = self.project_key + "_BOOTSTRAP_VERSION"
        self.timestamp = datetime.now().isoformat()

    @staticmethod
    def _extract_key(project_name: str) -> str:
        """Extract 2-3 letter key from project name (capital letters)."""
        key = ''.join([c for c in project_name if c.isupper()])

        if len(key) >= 2:
            return key[:3]

        return project_name[:3].upper() if len(project_name) >= 2 else project_name.upper()

    def get_replacements(self) -> dict:
        """Return all replacement patterns for branding injection."""
        return {
            "NileAndSinai": self.project_name,
            "NSA": self.project_key,
            "nsa_": self.project_prefix,
            "NileAndSinaiBootstrap": self.bootstrap_class,
            "NSA_BOOTSTRAP_VERSION": self.version_constant,
            "_nsa_": "_" + self.project_prefix,
            "[NileAndSinai": "[" + self.project_name,
        }

    def to_dict(self) -> dict:
        """Return branding as dictionary for documentation."""
        return {
            "projectName": self.project_name,
            "projectKey": self.project_key,
            "projectPrefix": self.project_prefix,
            "bootstrapClass": self.bootstrap_class,
            "versionConstant": self.version_constant,
            "timestamp": self.timestamp,
        }

# ---------- Enhanced UI Components ----------
class AnimatedButton(QPushButton):
    """Button with smooth hover and press animations"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(44)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self._shadow = QGraphicsDropShadowEffect(blurRadius=20, xOffset=0, yOffset=6)
        self._shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self._shadow)
        self._setup_animations()

    def _setup_animations(self):
        self.anim_hover = QPropertyAnimation(self._shadow, b"blurRadius")
        self.anim_hover.setDuration(200)
        self.anim_hover.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        self.anim_hover.setEndValue(30)
        self.anim_hover.start()
        self.setStyleSheet(self.hover_style())
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim_hover.setEndValue(20)
        self.anim_hover.start()
        self.setStyleSheet(self.default_style())
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.setStyleSheet(self.pressed_style())
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setStyleSheet(self.hover_style() if self.underMouse() else self.default_style())
        super().mouseReleaseEvent(event)

    def default_style(self):
        return """
            AnimatedButton {
                border-radius: 10px;
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                             stop:0 #2d3748, stop:1 #1a202c);
                color: #e2e8f0;
                border: 1px solid rgba(255, 255, 255, 0.08);
                font-weight: 600;
                font-size: 14px;
            }
        """

    def hover_style(self):
        return """
            AnimatedButton {
                border-radius: 10px;
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                             stop:0 #4c9aff, stop:1 #2563eb);
                color: #ffffff;
                border: 1px solid rgba(79, 172, 254, 0.5);
                font-weight: 600;
                font-size: 14px;
            }
        """

    def pressed_style(self):
        return """
            AnimatedButton {
                border-radius: 10px;
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                             stop:0 #1f5fbf, stop:1 #1847a0);
                color: #ffffff;
                border: 1px solid #0f4fc0;
                font-weight: 600;
                font-size: 14px;
            }
        """

class StatsCard(QFrame):
    """Statistics card for dashboard"""
    def __init__(self, title, value, icon="", color="#4f46e5"):
        super().__init__()
        self.setFixedHeight(120)
        self.setFrameShape(QFrame.NoFrame)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Normal))
        title_label.setStyleSheet(f"color: #9ca3af; font-weight: 600;")

        # Value with icon
        value_layout = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI", 14))
            value_layout.addWidget(icon_label)

        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_layout.addWidget(value_label)
        value_layout.addStretch()

        layout.addWidget(title_label)
        layout.addLayout(value_layout)

        self.setStyleSheet("""
            StatsCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 rgba(45, 55, 72, 0.8), stop:1 rgba(26, 32, 44, 0.9));
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 12px;
            }
        """)

class BrandingPreviewCard(QFrame):
    """Card showing real-time branding preview"""
    def __init__(self):
        super().__init__()
        self.setFixedHeight(140)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 #1e3a8a, stop:1 #0f172a);
                border: 2px solid #3b82f6;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title = QLabel("📋 Branding Preview")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet("color: #93c5fd;")
        layout.addWidget(title)

        self.key_label = QLabel("Project Key: ?")
        self.key_label.setFont(QFont("Courier New", 11))
        self.key_label.setStyleSheet("color: #dbeafe; padding: 4px;")
        layout.addWidget(self.key_label)

        self.prefix_label = QLabel("Function Prefix: ?")
        self.prefix_label.setFont(QFont("Courier New", 11))
        self.prefix_label.setStyleSheet("color: #dbeafe; padding: 4px;")
        layout.addWidget(self.prefix_label)

        self.class_label = QLabel("Bootstrap Class: ?Bootstrap")
        self.class_label.setFont(QFont("Courier New", 11))
        self.class_label.setStyleSheet("color: #dbeafe; padding: 4px;")
        layout.addWidget(self.class_label)

        layout.addStretch()

    def update_branding(self, branding):
        if branding:
            self.key_label.setText(f"🔑 Project Key: {branding.project_key}")
            self.prefix_label.setText(f"⚙️  Function Prefix: {branding.project_prefix}")
            self.class_label.setText(f"📦 Bootstrap Class: {branding.bootstrap_class}")
        else:
            self.key_label.setText("🔑 Project Key: ?")
            self.prefix_label.setText("⚙️  Function Prefix: ?")
            self.class_label.setText("📦 Bootstrap Class: ?Bootstrap")

class RecentProjectsWidget(QFrame):
    """Widget showing recent projects"""
    project_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: rgba(45, 55, 72, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("📂 Recent Projects")
        title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title.setStyleSheet("color: #e2e8f0;")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        self.list_widget.setMaximumHeight(200)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 6px;
                margin: 3px 0px;
            }
            QListWidget::item:hover {
                background: rgba(79, 172, 254, 0.1);
            }
            QListWidget::item:selected {
                background: rgba(79, 172, 254, 0.2);
            }
        """)
        self.list_widget.itemClicked.connect(self._on_project_selected)
        layout.addWidget(self.list_widget)

    def add_projects(self, projects):
        self.list_widget.clear()
        for project in projects[-5:]:  # Show last 5
            item = QListWidgetItem(f"📁 {project['name']} • {project['date']}")
            item.setData(Qt.UserRole, project['path'])
            self.list_widget.addItem(item)

    def _on_project_selected(self, item):
        path = item.data(Qt.UserRole)
        self.project_selected.emit(path)

# ---------- Worker to run creation in background ----------
class CreatorWorker(QObject):
    progress = pyqtSignal(int)
    log = pyqtSignal(str, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, base_path: str, structure: dict, extras: dict, branding: ProjectBranding = None):
        super().__init__()
        self.base_path = base_path
        self.structure = structure
        self.extras = extras
        self.branding = branding
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            total = self._count_tasks(self.structure)
            extras_count = 0
            if self.extras.get("readme"): extras_count += 1
            if self.extras.get("gitignore"): extras_count += 1
            if self.extras.get("init_git"): extras_count += 1
            if self.extras.get("venv"): extras_count += 1
            if self.extras.get("copy_connector"): extras_count += 1
            if self.extras.get("branding_doc"): extras_count += 1
            total += extras_count

            if total == 0:
                self.log.emit("Nothing to create.", "")
                self.finished.emit(True, "Nothing to create")
                return

            tasks_done = 0

            def emit_progress():
                pct = int((tasks_done / total) * 100)
                self.progress.emit(pct)

            os.makedirs(self.base_path, exist_ok=True)
            self.log.emit(f"✓ Project folder prepared", self.base_path)
            tasks_done += 1
            emit_progress()

            for root, dirs, files in self._iter_structure(self.base_path, self.structure):
                if self._is_cancelled:
                    self.finished.emit(False, "Cancelled by user")
                    return
                for d in dirs:
                    path_d = os.path.join(root, d)
                    os.makedirs(path_d, exist_ok=True)
                    tasks_done += 1
                    self.log.emit(f"✓ Created: {d}/", d)
                    emit_progress()
                for f in files:
                    path_f = os.path.join(root, f)
                    os.makedirs(os.path.dirname(path_f), exist_ok=True)
                    if not os.path.exists(path_f):
                        with open(path_f, "w", encoding="utf-8") as fh:
                            if f.lower().endswith(".php"):
                                fh.write("<?php\n// auto-generated\n?>\n")
                            elif f.lower().endswith(".md"):
                                fh.write(f"# {os.path.basename(self.base_path)}\n")
                        self.log.emit(f"✓ Created: {f}", f)
                    else:
                        self.log.emit(f"⊘ File exists: {f}", f)
                    tasks_done += 1
                    emit_progress()

            if self.extras.get("copy_connector") and self.branding:
                self._copy_and_inject_connector(tasks_done, total, emit_progress)
                tasks_done += 1
                emit_progress()

            if self.extras.get("readme"):
                path = os.path.join(self.base_path, "README.md")
                if not os.path.exists(path):
                    with open(path, "w", encoding="utf-8") as fh:
                        fh.write(f"# {os.path.basename(self.base_path)}\n\nGenerated on {datetime.now().isoformat()}\n")
                self.log.emit(f"✓ Created: README.md", "README.md")
                tasks_done += 1
                emit_progress()

            if self.extras.get("gitignore"):
                path = os.path.join(self.base_path, ".gitignore")
                if not os.path.exists(path):
                    with open(path, "w", encoding="utf-8") as fh:
                        fh.write("venv/\n__pycache__/\n*.pyc\n.DS_Store\n.env\n*.db\n")
                self.log.emit(f"✓ Created: .gitignore", ".gitignore")
                tasks_done += 1
                emit_progress()

            if self.extras.get("venv"):
                venv_path = os.path.join(self.base_path, "venv")
                os.makedirs(venv_path, exist_ok=True)
                self.log.emit(f"✓ Created: venv/", "venv")
                tasks_done += 1
                emit_progress()

            if self.extras.get("init_git"):
                try:
                    subprocess.run(["git", "init", self.base_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.log.emit("✓ Initialized git repository", "git init")
                except Exception as e:
                    self.log.emit(f"⊘ Git init unavailable", "git init")
                tasks_done += 1
                emit_progress()

            if self.extras.get("branding_doc") and self.branding:
                self._create_branding_context(tasks_done, total, emit_progress)
                tasks_done += 1
                emit_progress()

            self.progress.emit(100)
            self.finished.emit(True, "✓ Project created successfully!")
        except Exception as exc:
            self.finished.emit(False, f"✗ Error: {exc}")

    def _copy_and_inject_connector(self, tasks_done: int, total: int, emit_progress):
        """Copy Connector folder and inject project-specific branding."""
        source_connector = os.path.join(
            os.path.dirname(__file__), "Connector"
        )
        dest_connector = os.path.join(self.base_path, "Assets", "Connector")

        if not os.path.exists(source_connector):
            self.log.emit(f"⊘ Connector framework not found", "Connector")
            return

        os.makedirs(dest_connector, exist_ok=True)
        self._copy_tree(source_connector, dest_connector)
        self.log.emit(f"✓ Copied Connector framework", "Connector")

        if self.branding:
            self._inject_branding_recursive(dest_connector)
            self.log.emit(f"✓ Injected branding: {self.branding.project_key}", "Branding")

    def _copy_tree(self, src: str, dst: str):
        """Recursively copy directory tree."""
        for item in os.listdir(src):
            src_path = os.path.join(src, item)
            dst_path = os.path.join(dst, item)

            if os.path.isdir(src_path):
                os.makedirs(dst_path, exist_ok=True)
                self._copy_tree(src_path, dst_path)
            else:
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                if not os.path.exists(dst_path):
                    with open(src_path, 'rb') as f:
                        content = f.read()
                    with open(dst_path, 'wb') as f:
                        f.write(content)

    def _inject_branding_recursive(self, base_path: str):
        """Recursively inject branding into all PHP files."""
        replacements = self.branding.get_replacements()

        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.php'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        for old, new in replacements.items():
                            content = content.replace(old, new)

                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                    except Exception as e:
                        self.log.emit(f"⊘ Error in {file}: {e}", file)

    def _create_branding_context(self, tasks_done: int, total: int, emit_progress):
        """Create CONNECTOR_BRANDING_CONTEXT.md for this project."""
        doc_path = os.path.join(self.base_path, "CONNECTOR_BRANDING_CONTEXT.md")

        branding_info = self.branding.to_dict()

        doc_content = f"""# {self.branding.project_name} - Connector Branding Context

**Project Name:** {branding_info['projectName']}
**Project Key:** {branding_info['projectKey']}
**Function Prefix:** `{branding_info['projectPrefix']}`
**Bootstrap Class:** `{branding_info['bootstrapClass']}`
**Version Constant:** `{branding_info['versionConstant']}`
**Created:** {branding_info['timestamp']}

## Quick Reference

All global functions start with `{branding_info['projectPrefix']}`:

- `{branding_info['projectPrefix']}bootstrap()` - Initialize Connector
- `{branding_info['projectPrefix']}db()` - Get PDO instance
- `{branding_info['projectPrefix']}config()` - Get configuration
- `{branding_info['projectPrefix']}log_error()` - Log errors

## Usage Example

```php
<?php
declare(strict_types=1);
require_once dirname(__DIR__, 4) . '/Connector/_bootstrap.php';

{branding_info['projectPrefix']}bootstrap(['security' => true, 'session' => true]);
$pdo = {branding_info['projectPrefix']}db();
```

---

For full documentation, see CONNECTOR_BRANDING_GUIDE.md
"""

        try:
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            self.log.emit(f"✓ Created: CONNECTOR_BRANDING_CONTEXT.md", "Branding Doc")
        except Exception as e:
            self.log.emit(f"⊘ Error creating branding doc: {e}", "Error")

    def _count_tasks(self, structure):
        total = 0
        for key, val in structure.items():
            total += 1
            if isinstance(val, dict):
                total += self._count_tasks(val)
            elif isinstance(val, (list, set, tuple)):
                total += len(val)
            elif val is None:
                total += 1
        return total

    def _iter_structure(self, base_path, structure):
        """Yields tuples (root_path, [dirs], [files]) similar to os.walk"""
        stack = [(base_path, structure)]
        while stack:
            root, struct = stack.pop(0)
            dirs = []
            files = []
            for name, content in struct.items():
                if isinstance(content, dict):
                    dirs.append(name)
                elif isinstance(content, (list, set, tuple)):
                    dirs.append(name)
                elif content is None:
                    files.append(name)
            yield root, dirs, files
            for name, content in struct.items():
                if isinstance(content, dict):
                    stack.append((os.path.join(root, name), content))
                elif isinstance(content, (list, set, tuple)):
                    inner_files = list(content)
                    yield os.path.join(root, name), [], inner_files

# ---------- Main Application ----------
class ModernDirectoryCreator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 AutoMatic File Generator v2.1 - Professional Project Creator")
        self.setGeometry(50, 50, 1500, 1000)
        self.setMinimumSize(1300, 900)
        self.setWindowIcon(QIcon())

        self.db_connection = sqlite3.connect("directory_logs_modern.db")
        self._create_logs_table()

        self.user_system_name = platform.node()
        self.selected_directory = None
        self.branding = None
        self.recent_projects = self._load_recent_projects()

        self._setup_ui()
        self._apply_styles()

        self.worker_thread = None
        self.worker = None

    def _create_logs_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            project_name TEXT,
                            user TEXT,
                            timestamp TEXT,
                            path TEXT)''')
        self.db_connection.commit()

    def _load_recent_projects(self):
        """Load recent projects from database"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('SELECT project_name, timestamp, path FROM logs ORDER BY id DESC LIMIT 10')
            rows = cursor.fetchall()
            return [{'name': r[0], 'date': r[1][:10], 'path': r[2]} for r in rows]
        except:
            return []

    def _setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left sidebar
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel, 1)

        # Right content area
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel, 2)

        self.setLayout(main_layout)

    def _create_left_panel(self):
        """Create left sidebar with stats and recent projects"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 #0f172a, stop:1 #0b0e1a);
                border-right: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = QLabel("📊 Dashboard")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("color: #e2e8f0;")
        layout.addWidget(header)

        # Stats
        total_projects = len(self.recent_projects)
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM logs")
        total_count = cursor.fetchone()[0]

        stats_grid = QGridLayout()
        stats_grid.setSpacing(12)

        stat1 = StatsCard("Total Projects", total_count, "📁", "#4f46e5")
        stat2 = StatsCard("Recent", total_projects, "⏱️", "#0ea5e9")
        stats_grid.addWidget(stat1, 0, 0)
        stats_grid.addWidget(stat2, 0, 1)

        layout.addLayout(stats_grid)

        # Recent projects
        if self.recent_projects:
            self.recent_widget = RecentProjectsWidget()
            self.recent_widget.add_projects(self.recent_projects)
            layout.addWidget(self.recent_widget)

        layout.addStretch()

        # Footer info
        footer = QLabel(f"👤 {self.user_system_name}\n🖥️ {platform.system()}")
        footer.setFont(QFont("Segoe UI", 9))
        footer.setStyleSheet("color: #64748b;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

        return panel

    def _create_right_panel(self):
        """Create main right panel with creation form"""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # Header with title and version
        header_layout = QHBoxLayout()
        title = QLabel("🚀 Create New Project")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #e2e8f0;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        version_badge = QLabel("v2.1")
        version_badge.setFont(QFont("Segoe UI", 10, QFont.Bold))
        version_badge.setStyleSheet("""
            QLabel {
                background: #4f46e5;
                color: white;
                padding: 4px 12px;
                border-radius: 20px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(version_badge)
        layout.addLayout(header_layout)

        # Main form in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background: rgba(255, 255, 255, 0.02);
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(79, 172, 254, 0.3);
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(79, 172, 254, 0.5);
            }
        """)

        scroll_content = QWidget()
        form_layout = QVBoxLayout(scroll_content)
        form_layout.setSpacing(20)

        # Project name section
        form_layout.addWidget(self._create_section_title("📝 Project Information"))

        name_grid = QGridLayout()
        name_grid.setSpacing(15)

        name_grid.addWidget(QLabel("Project Name:"), 0, 0, alignment=Qt.AlignRight)
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("e.g., NileAndSinai, MyAwesomeProject")
        self.project_name_input.setMinimumHeight(44)
        self.project_name_input.textChanged.connect(self.on_project_name_changed)
        name_grid.addWidget(self.project_name_input, 0, 1)

        name_grid.addWidget(QLabel("Template:"), 1, 0, alignment=Qt.AlignRight)
        self.template_combo = QComboBox()
        self.template_combo.addItem("🌐 Default Website Template")
        self.template_combo.addItem("🔌 Microservice / API Template")
        self.template_combo.setMinimumHeight(44)
        name_grid.addWidget(self.template_combo, 1, 1)

        form_layout.addLayout(name_grid)

        # Branding preview
        self.branding_preview = BrandingPreviewCard()
        form_layout.addWidget(self.branding_preview)

        # Directory selection
        form_layout.addWidget(self._create_section_title("📂 Project Location"))

        dir_layout = QHBoxLayout()
        self.dir_select_button = AnimatedButton("📁 Browse Directory")
        self.dir_select_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_select_button)

        self.selected_dir_label = QLabel("No directory selected")
        self.selected_dir_label.setStyleSheet("color: #9ca3af; font-style: italic;")
        self.selected_dir_label.setWordWrap(True)
        dir_layout.addWidget(self.selected_dir_label, 1)
        form_layout.addLayout(dir_layout)

        # Options section
        form_layout.addWidget(self._create_section_title("⚙️ Configuration"))

        options_grid = QGridLayout()
        options_grid.setSpacing(12)

        col = 0
        options = [
            ("Create README.md", True, "readme"),
            ("Create .gitignore", True, "gitignore"),
            ("Initialize Git Repository", False, "init_git"),
            ("Create Python venv", False, "venv"),
            ("Copy & Inject Connector", True, "copy_connector"),
            ("Create Branding Docs", True, "branding_doc"),
            ("Open Folder After Creation", False, "open_after"),
        ]

        self.checkboxes = {}
        for i, (label, checked, key) in enumerate(options):
            checkbox = QCheckBox(label)
            checkbox.setChecked(checked)
            checkbox.setStyleSheet("""
                QCheckBox {
                    spacing: 8px;
                    color: #e2e8f0;
                    font-size: 13px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
            """)
            self.checkboxes[key] = checkbox
            row = i // 2
            col = i % 2
            options_grid.addWidget(checkbox, row, col)

        form_layout.addLayout(options_grid)

        # Action buttons
        form_layout.addSpacing(30)
        form_layout.addWidget(self._create_section_title("💡 Action"))

        btn_layout = QHBoxLayout()

        self.create_button = AnimatedButton("✨ Create Project")
        self.create_button.setMinimumHeight(50)
        self.create_button.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.create_button.clicked.connect(self.on_create_clicked)
        btn_layout.addWidget(self.create_button)

        self.cancel_button = AnimatedButton("✕ Cancel")
        self.cancel_button.setMinimumHeight(50)
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        btn_layout.addWidget(self.cancel_button)

        form_layout.addLayout(btn_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 3px;
                margin-top: 15px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                           stop:0 #4f46e5, stop:1 #0ea5e9);
                border-radius: 3px;
            }
        """)
        form_layout.addWidget(self.progress_bar)

        # Activity log
        form_layout.addWidget(self._create_section_title("📋 Activity Log"))

        self.logs_area = QTextEdit()
        self.logs_area.setReadOnly(True)
        self.logs_area.setMinimumHeight(250)
        self.logs_area.setMaximumHeight(300)
        self.logs_area.setStyleSheet("""
            QTextEdit {
                background: #0f172a;
                color: #9fffb0;
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 10px;
                font-family: 'Courier New';
                font-size: 12px;
                selection-background-color: rgba(79, 172, 254, 0.3);
            }
        """)
        form_layout.addWidget(self.logs_area)

        # Export buttons
        btn_row = QHBoxLayout()

        self.export_logs_btn = AnimatedButton("📥 Export Logs (CSV)")
        self.export_logs_btn.clicked.connect(self.export_logs)
        btn_row.addWidget(self.export_logs_btn)

        self.show_db_logs_btn = AnimatedButton("📊 Recent Logs")
        self.show_db_logs_btn.clicked.connect(self.show_db_logs_dialog)
        btn_row.addWidget(self.show_db_logs_btn)

        btn_row.addStretch()
        form_layout.addLayout(btn_row)

        form_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)

        return panel

    def _create_section_title(self, text):
        """Create a styled section title"""
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        label.setStyleSheet("color: #cbd5e1; margin-top: 5px; margin-bottom: 5px;")
        return label

    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #0b0e1a, stop:1 #0f1417);
                color: #e2e8f0;
                font-family: "Segoe UI", Arial;
            }
            QLineEdit, QComboBox {
                background: #1a202c;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 10px 12px;
                border-radius: 8px;
                color: #e2e8f0;
                selection-background-color: rgba(79, 172, 254, 0.4);
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #4f46e5;
                background: #1e2938;
            }
            QLineEdit::placeholder {
                color: #64748b;
            }
            QCheckBox {
                color: #cbd5e1;
                spacing: 8px;
            }
            QCheckBox::indicator:unchecked {
                background: #1a202c;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background: #4f46e5;
                border: 1px solid #4f46e5;
                border-radius: 4px;
                width: 18px;
                height: 18px;
                image: url(:/check);
            }
            QLabel {
                color: #e2e8f0;
            }
            QMessageBox {
                background: #0b0e1a;
            }
            QMessageBox QLabel {
                color: #e2e8f0;
            }
        """)

    def on_project_name_changed(self):
        """Update branding preview as user types project name"""
        project_name = self.project_name_input.text().strip()
        if project_name:
            self.branding = ProjectBranding(project_name)
            self.branding_preview.update_branding(self.branding)
        else:
            self.branding = None
            self.branding_preview.update_branding(None)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Parent Directory", os.path.expanduser("~"))
        if directory:
            self.selected_directory = directory
            display_path = directory if len(directory) < 80 else "..." + directory[-77:]
            self.selected_dir_label.setText(display_path)
            self.append_log(f"✓ Selected: {directory}", directory)
            self.progress_bar.setValue(0)

    def on_create_clicked(self):
        project_name = self.project_name_input.text().strip()
        if not project_name:
            QMessageBox.warning(self, "⚠️ Input Error", "Please enter a project name.")
            return
        if not self.selected_directory:
            QMessageBox.warning(self, "⚠️ Input Error", "Please select a parent directory.")
            return

        project_path = os.path.join(self.selected_directory, project_name)
        if os.path.exists(project_path):
            resp = QMessageBox.question(self, "⚠️ Project Exists",
                f"Project already exists:\n{project_path}\n\nContinue?",
                QMessageBox.Yes | QMessageBox.No)
            if resp == QMessageBox.No:
                return

        template_name = self.template_combo.currentText()
        structure = self._get_template_structure(template_name)

        extras = {
            "readme": self.checkboxes["readme"].isChecked(),
            "gitignore": self.checkboxes["gitignore"].isChecked(),
            "init_git": self.checkboxes["init_git"].isChecked(),
            "venv": self.checkboxes["venv"].isChecked(),
            "copy_connector": self.checkboxes["copy_connector"].isChecked(),
            "branding_doc": self.checkboxes["branding_doc"].isChecked(),
            "open_after": self.checkboxes["open_after"].isChecked(),
        }

        self.create_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.logs_area.clear()

        self.worker = CreatorWorker(project_path, structure, extras, self.branding)
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

        self.append_log(f"🚀 Started creation: {project_name}", project_name)

    def on_cancel_clicked(self):
        if self.worker:
            self.worker.cancel()
            self.append_log("⏸️  Cancellation requested...", "")
            self.cancel_button.setEnabled(False)

    def on_progress(self, val: int):
        self.progress_bar.setValue(val)

    def on_finished(self, success: bool, message: str):
        self.append_log(message, "")
        self.create_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(100 if success else 0)

        if self.selected_directory:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor = self.db_connection.cursor()
            cursor.execute('INSERT INTO logs (project_name, user, timestamp, path) VALUES (?, ?, ?, ?)',
                           (self.project_name_input.text().strip(), self.user_system_name, timestamp, self.selected_directory))
            self.db_connection.commit()

        if success and self.checkboxes["open_after"].isChecked():
            try:
                path_to_open = os.path.join(self.selected_directory, self.project_name_input.text().strip())
                if sys.platform == "win32":
                    os.startfile(path_to_open)
                elif sys.platform == "darwin":
                    subprocess.run(["open", path_to_open])
                else:
                    subprocess.run(["xdg-open", path_to_open])
            except Exception as e:
                self.append_log(f"⊘ Could not open folder: {e}", "")

        icon = "✓" if success else "✗"
        QMessageBox.information(self, f"{icon} Finished", message)

    def append_log(self, message: str, name: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.logs_area.append(f"[{ts}] {message}")
        if name:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('INSERT INTO logs (project_name, user, timestamp, path) VALUES (?, ?, ?, ?)',
                               (name, self.user_system_name, ts, self.selected_directory or ""))
                self.db_connection.commit()
            except Exception:
                pass

    def export_logs(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Logs CSV", os.path.expanduser("~/automation_logs.csv"), "CSV Files (*.csv)")
        if not path:
            return
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id, project_name, user, timestamp, path FROM logs")
            rows = cursor.fetchall()
            with open(path, "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(["ID", "Project Name", "User", "Timestamp", "Path"])
                writer.writerows(rows)
            QMessageBox.information(self, "✓ Success", f"Logs exported to:\n{path}")
        except Exception as e:
            QMessageBox.warning(self, "✗ Export Failed", str(e))

    def show_db_logs_dialog(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT id, project_name, user, timestamp FROM logs ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()
        text = "\n".join([f"#{r[0]:3} | {r[1]:20} | {r[2]:15} | {r[3]}" for r in rows]) or "(no logs)"

        dialog = QDialog(self)
        dialog.setWindowTitle("📊 Recent Project Creation Logs")
        dialog.setGeometry(200, 200, 800, 500)
        layout = QVBoxLayout(dialog)

        text_edit = QTextEdit()
        text_edit.setText(text)
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Courier New", 10))
        layout.addWidget(text_edit)

        close_btn = AnimatedButton("✕ Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec_()

    def closeEvent(self, event):
        try:
            self.db_connection.close()
        except Exception:
            pass
        event.accept()

    def _get_template_structure(self, template_name: str):
        """Updated template structure based on patterns"""
        default = {
            'Assets': {
                'Website': {
                    'Contents': {
                        'Landing': {},
                        'Pages': {},
                    },
                    'Pages': [
                        'index.php',
                        'about-us.php',
                        'contact.php',
                        'faqs.php',
                        'privacy-policy.php',
                        'terms-conditions.php',
                    ],
                    'Api': {
                        'V1': {
                            'Pages': [
                                'contact-engine.php',
                                'faqs-engine.php',
                            ],
                        },
                    },
                    'Images': {},
                    'Scripts': ['main.js'],
                    'Styles': ['main.css'],
                    'Videos': {},
                },

                'Accounts': {
                    'Contents': {
                        'Auth': {},
                        'Profile': {},
                        'Dashboard': {},
                    },
                    'Pages': [
                        'login.php',
                        'register.php',
                        'dashboard.php',
                        'profile.php',
                        'settings.php',
                    ],
                    'Api': {
                        'V1': {
                            'Auth': [
                                'login.php',
                                'register.php',
                                'logout.php',
                                'me.php',
                                'csrf.php',
                            ],
                            'Profile': [
                                'overview.php',
                                'update.php',
                                'picture.php',
                            ],
                            'Dashboard': [
                                'overview.php',
                            ],
                            'Settings': [
                                'overview.php',
                                'update.php',
                                'password.php',
                            ],
                        },
                    },
                    'Scripts': ['accounts.js'],
                    'Styles': ['accounts.css'],
                },

                'Admins': {
                    'Contents': {
                        'Dashboard': {},
                        'Analytics': {},
                        'Management': {},
                    },
                    'Pages': [
                        'login.php',
                        'dashboard.php',
                        'analytics.php',
                        'users.php',
                        'settings.php',
                    ],
                    'Api': {
                        'V1': {
                            'Auth': [
                                'login.php',
                                'logout.php',
                                'me.php',
                            ],
                            'Dashboard': [
                                'stats.php',
                                'overview.php',
                            ],
                            'Users': [
                                'list.php',
                                'get.php',
                                'update.php',
                            ],
                        },
                    },
                    'Scripts': ['admin.js'],
                    'Styles': ['admin.css'],
                },

                'Services': {
                    'Accounts': {
                        '__init__.php': None,
                    },
                    'Auth': {
                        '__init__.php': None,
                    },
                    'Products': {
                        '__init__.php': None,
                    },
                    'Email': {
                        '__init__.php': None,
                    },
                },

                'Modules': {
                    'nav.php': None,
                    'footer.php': None,
                    'seo.php': None,
                    'base.css': None,
                    'shared-scripts.js': None,
                },

                'Extras': {
                    'Documentations': {
                        'README.md': None,
                    },
                    'Sqls': {
                        'auth_schema_v1.sql': None,
                        'migrations.md': None,
                    },
                    'Updates': {
                        'CHANGELOG.md': None,
                    },
                    'Connections': {},
                },

                'Miscellaneous': {
                    'Context': {},
                    'Information': {},
                    'Testing': {},
                },
            },

            'index.php': None,
            '.env': None,
            '.env.example': None,
            'composer.json': None,
            'composer.lock': None,
            '.gitignore': None,
            '.htaccess': None,
        }

        microservice = {
            'src': {
                'Api': {
                    'V1': {
                        'Controllers': {},
                        'Middleware': {},
                    },
                },
                'Services': {},
                'Models': {},
                'Database': {},
                'Utils': {},
            },
            'config': {
                'app.php': None,
                'database.php': None,
            },
            'tests': {
                'Unit': {},
                'Integration': {},
            },
            'docs': {
                'API.md': None,
            },
            'public': {
                'index.php': None,
            },
            'Dockerfile': None,
            'docker-compose.yml': None,
            '.env': None,
            '.env.example': None,
            'composer.json': None,
        }

        if "micro" in template_name.lower():
            return microservice
        return default

# ---------- Main Entry Point ----------
def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    w = ModernDirectoryCreator()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
