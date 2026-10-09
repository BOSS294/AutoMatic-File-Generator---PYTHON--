# modern_directory_creator.py
"""
AutoMatic File Generator - Professional Project Structure Generator with Intelligent Branding
Version: 2.0.0
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
    QTimer, QRect, QPoint, QEvent
)
from PyQt5.QtGui import (
    QFont, QIcon, QCursor, QColor, QPalette, QBrush, QPixmap, QPainter
)
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox, QCheckBox,
    QFrame, QSpacerItem, QSizePolicy, QGridLayout, QScrollArea, QListWidget,
    QListWidgetItem, QDialog, QTabWidget, QStyledItemDelegate
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
        # First try: take all capital letters
        key = ''.join([c for c in project_name if c.isupper()])

        if len(key) >= 2:
            return key[:3]  # Cap at 3 letters

        # Fallback: take first 2-3 letters and uppercase
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

# ---------- Worker to run creation in background ----------
class CreatorWorker(QObject):
    progress = pyqtSignal(int)
    log = pyqtSignal(str, str)  # message, directory/file name
    finished = pyqtSignal(bool, str)  # success, message

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
            # extras add a few tasks
            extras_count = 0
            if self.extras.get("readme"): extras_count += 1
            if self.extras.get("gitignore"): extras_count += 1
            if self.extras.get("init_git"): extras_count += 1
            if self.extras.get("venv"): extras_count += 1
            if self.extras.get("open_after"): extras_count += 0
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

            # Copy and inject Connector if needed
            if self.extras.get("copy_connector") and self.branding:
                self._copy_and_inject_connector(tasks_done, total, emit_progress)
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
                os.makedirs(venv_path, exist_ok=True)
                self.log.emit(f"Created placeholder venv folder: {venv_path}", "venv")
                tasks_done += 1
                emit_progress()

            if self.extras.get("init_git"):
                try:
                    subprocess.run(["git", "init", self.base_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.log.emit("Initialized git repository.", "git init")
                except Exception as e:
                    self.log.emit(f"Git init failed or not available: {e}", "git init")
                tasks_done += 1
                emit_progress()

            # Create branding documentation
            if self.extras.get("branding_doc") and self.branding:
                self._create_branding_context(tasks_done, total, emit_progress)
                tasks_done += 1
                emit_progress()

            self.progress.emit(100)
            self.finished.emit(True, "Creation finished successfully")
        except Exception as exc:
            self.finished.emit(False, f"Failed: {exc}")

    def _copy_and_inject_connector(self, tasks_done: int, total: int, emit_progress):
        """Copy Connector folder and inject project-specific branding."""
        source_connector = os.path.join(
            os.path.dirname(__file__), "Connector"
        )
        dest_connector = os.path.join(self.base_path, "Assets", "Connector")

        if not os.path.exists(source_connector):
            self.log.emit(f"Warning: Source Connector not found at {source_connector}", "Connector")
            return

        # Copy Connector tree
        os.makedirs(dest_connector, exist_ok=True)
        self._copy_tree(source_connector, dest_connector)
        self.log.emit(f"Copied Connector framework", "Connector")

        # Inject branding into all PHP files
        if self.branding:
            self._inject_branding_recursive(dest_connector)
            self.log.emit(f"Injected branding: {self.branding.project_name} ({self.branding.project_key})", "Branding")

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

                        # Apply all replacements
                        for old, new in replacements.items():
                            content = content.replace(old, new)

                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)

                        self.log.emit(f"Injected branding in: {file}", file)
                    except Exception as e:
                        self.log.emit(f"Error injecting branding in {file}: {e}", file)

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

---

## Quick Reference

All global functions start with `{branding_info['projectPrefix']}`:

### Core Functions
- `{branding_info['projectPrefix']}bootstrap()` - Initialize Connector with options
- `{branding_info['projectPrefix']}db()` - Get PDO database instance
- `{branding_info['projectPrefix']}config(key, default)` - Retrieve configuration value
- `{branding_info['projectPrefix']}log_error(message)` - Log error to system

### Usage Example
```php
<?php
declare(strict_types=1);

require_once dirname(__DIR__, 4) . '/Connector/_bootstrap.php';

{branding_info['projectPrefix']}bootstrap([
    'security' => true,
    'session' => true,
    'methods' => ['GET', 'POST'],
    'json' => true,
]);

$pdo = {branding_info['projectPrefix']}db();
$config = {branding_info['projectPrefix']}config('APP_ENV', 'production');
```

---

## File Header Pattern

Every Connector file begins with:

```php
/**
 * {branding_info['projectName']} - [Component Description]
 * Version: 2.0.0
 *
 * [Component-specific documentation]
 */
```

Example:
```php
/**
 * {branding_info['projectName']} - CSRF Protection
 * Version: 2.0.0
 *
 * Prevents cross-site request forgery attacks...
 */
```

---

## Session & Cookie Keys

All session-related keys are prefixed with `_{branding_info['projectPrefix']}`:

- CSRF Token: `_{branding_info['projectPrefix']}csrf_token`
- Device Fingerprint: `_{branding_info['projectPrefix']}fingerprint`
- Session: `_{branding_info['projectPrefix']}session_id`

---

## Bootstrap Class

All Connector initialization routes through:

```php
final class {branding_info['bootstrapClass']}
{{
    public static function load(): void {{ ... }}
    public static function boot(array $options = []): array {{ ... }}
    public static function db(): PDO {{ ... }}
}}
```

### Static Methods
- `{branding_info['bootstrapClass']}::load()` - Load all Connector classes
- `{branding_info['bootstrapClass']}::boot(options)` - Boot with specific options
- `{branding_info['bootstrapClass']}::db()` - Get PDO connection

---

## Version Constant

The Connector infrastructure version for this project:

```php
const {branding_info['versionConstant']} = '2.0.0';
```

This constant is used internally to track compatibility. Do **not** change it manually; it's updated only when upgrading the Connector framework.

---

## Error Messages & Logging

Error messages follow this pattern:

```
[{branding_info['projectName']} Logger Failure] Operation failed
[{branding_info['projectName']} Blocker Logger Failure] Request blocked
```

All logging goes through the structured logger in `Assets/Connector/Logger/oLogger.php`.

---

## Connector File Structure

```
Assets/Connector/
├── _bootstrap.php              # Entry point (defines {branding_info['bootstrapClass']})
├── connector.php               # Base environment & security setup
│
├── Auth/                       # Authentication layer
│   ├── Session.php
│   ├── Jwt.php
│   ├── Token.php
│   └── Permissions.php
│
├── Database/                   # Database abstraction
│   ├── Database.php
│   ├── QueryBuilder.php
│   └── ConnectionPool.php
│
├── Security/                   # Security features
│   ├── Csrf.php
│   ├── Headers.php
│   ├── OriginValidator.php
│   ├── RateLimiter.php
│   ├── DeviceFingerprint.php
│   ├── RequestValidator.php
│   ├── RequestContext.php
│   └── Security.php
│
├── Logger/                     # Structured logging
│   ├── oLogger.php
│   └── LogTypes.php
│
├── Helpers/                    # Utility helpers
│   ├── Response.php
│   ├── Sanitizer.php
│   ├── Validator.php
│   └── Utilities.php
│
├── Services/                   # Service layer
│   ├── CacheService.php
│   ├── ConfigService.php
│   ├── HealthService.php
│   └── ApiExceptionHandler.php
│
└── Exceptions/                 # Exception hierarchy
    ├── AuthenticationException.php
    ├── AuthorizationException.php
    ├── ValidationException.php
    ├── RateLimitException.php
    └── SecurityException.php
```

---

## Creating New API Endpoints

Every API endpoint should follow this template:

```php
<?php
declare(strict_types=1);

require_once dirname(__DIR__, 4) . '/Connector/_bootstrap.php';

{branding_info['projectPrefix']}bootstrap([
    'security' => true,
    'session' => true,
    'methods' => ['GET', 'POST'],
    'json' => true,
]);

// 1. Authenticate
$userId = $_SESSION['user_id'] ?? null;
if (!$userId) {{
    {branding_info['projectPrefix']}json_response(['success' => false, 'message' => 'Unauthorized'], 401);
}}

// 2. Validate CSRF for state-changing operations
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {{
    $csrf = $_POST['csrf_token'] ?? $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '';
    if (!{branding_info['projectPrefix']}validate_csrf($csrf)) {{
        {branding_info['projectPrefix']}json_response(['success' => false, 'message' => 'CSRF validation failed'], 403);
    }}
}}

// 3. Process request
try {{
    $pdo = {branding_info['projectPrefix']}db();
    // Your business logic here

    {branding_info['projectPrefix']}json_response(['success' => true, 'data' => $result]);
}} catch (Exception $e) {{
    {branding_info['projectPrefix']}log_error($e->getMessage());
    {branding_info['projectPrefix']}json_response(['success' => false, 'message' => 'Server error'], 500);
}}
```

---

## Important Notes for AI

This branding system exists to:

1. **Prevent naming collisions** when multiple projects coexist
2. **Maintain trademark consistency** across the codebase
3. **Provide instant context** about which project owns a function/class
4. **Enable automated testing** to verify no cross-project references exist

### Validation Commands

After any Connector changes, run these to ensure branding consistency:

```bash
# Verify all functions use correct prefix
grep -r "function {branding_info['projectPrefix']}_" Assets/Connector/

# Verify bootstrap class name
grep -r "final class {branding_info['bootstrapClass']}" Assets/Connector/

# Verify NO old prefixes remain
grep -r "nsa_\\|NSA\\|NileAndSinai" Assets/Connector/ # Should be EMPTY

# Verify version constant
grep -r "const {branding_info['versionConstant']}" Assets/Connector/
```

### Common Mistakes

- ❌ Forgetting to update session key prefixes (`_{branding_info['projectPrefix']}`)
- ❌ Leaving old project names in error messages
- ❌ Creating functions without the `{branding_info['projectPrefix']}_` prefix
- ❌ Manually editing Connector files that should be auto-generated

---

**Document Version:** 1.0.0
**For Next AI:** This document was auto-generated. Do not modify the branding patterns without reviewing CONNECTOR_BRANDING_GUIDE.md in the project root.

Reference: See `CONNECTOR_BRANDING_GUIDE.md` for comprehensive technical documentation.
"""

        try:
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            self.log.emit(f"Created: {doc_path}", "CONNECTOR_BRANDING_CONTEXT.md")
        except Exception as e:
            self.log.emit(f"Error creating branding context: {e}", "Error")

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
        """
        Yields tuples (root_path, [dirs], [files]) similar to os.walk but based
        on our nested structure dict.
        """
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

# ---------- UI helper widgets ----------
class HoverButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._shadow = QGraphicsDropShadowEffect(blurRadius=18, xOffset=0, yOffset=6)
        self._shadow.setColor(Qt.black)
        self.setGraphicsEffect(self._shadow)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self._anim = QPropertyAnimation(self._shadow, b"yOffset")
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
        self.setWindowTitle("🚀 AutoMatic File Generator - Professional Project Creator")
        self.setGeometry(100, 50, 1400, 900)
        self.setWindowIcon(QIcon())
        self.setMinimumSize(1200, 800)

        self.db_connection = sqlite3.connect("directory_logs_modern.db")
        self._create_logs_table()

        self.user_system_name = platform.node()
        self.selected_directory = None
        self.branding = None
        self.recent_projects = self._load_recent_projects()

        self._setup_ui()
        self._apply_styles()
        self._setup_animations()

        self.worker_thread = None
        self.worker = None

        # Welcome animation
        self.show_welcome_message()

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
        self.project_name_input.setPlaceholderText("Enter project name (e.g. NileAndSinai, MyProject)")
        self.project_name_input.setMinimumWidth(300)
        self.project_name_input.textChanged.connect(self.on_project_name_changed)

        self.branding_label = QLabel("Key: ?, Prefix: ?, Class: ?Bootstrap")
        self.branding_label.setStyleSheet("color: #9aa8b2; font-family: 'Courier New';")

        self.template_combo = QComboBox()
        self.template_combo.addItem("Default Website Template")
        self.template_combo.addItem("Microservice / API Template")
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
        self.chk_copy_connector = QCheckBox("✓ Copy & inject Connector layer")
        self.chk_branding_doc = QCheckBox("✓ Create branding context documentation")

        self.chk_readme.setChecked(True)
        self.chk_gitignore.setChecked(True)
        self.chk_copy_connector.setChecked(True)
        self.chk_branding_doc.setChecked(True)

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
        grid.addWidget(self.branding_label, 0, 2, 1, 2)

        grid.addWidget(QLabel("Template:"), 1, 0, alignment=Qt.AlignRight)
        grid.addWidget(self.template_combo, 1, 1, 1, 3)

        grid.addWidget(self.dir_select_button, 2, 0)
        grid.addWidget(self.selected_dir_label, 2, 1, 1, 3)

        # options area as a card-like frame
        card = QFrame()
        card_layout = QVBoxLayout()
        row1 = QHBoxLayout()
        row1.addWidget(self.chk_readme)
        row1.addWidget(self.chk_gitignore)
        row1.addWidget(self.chk_init_git)
        row1.addWidget(self.chk_venv)
        card_layout.addLayout(row1)
        row2 = QHBoxLayout()
        row2.addWidget(self.chk_open_after)
        row2.addWidget(self.chk_copy_connector)
        row2.addWidget(self.chk_branding_doc)
        card_layout.addLayout(row2)
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
                padding: 12px;
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

    def on_project_name_changed(self):
        """Update branding preview as user types project name."""
        project_name = self.project_name_input.text().strip()
        if project_name:
            self.branding = ProjectBranding(project_name)
            self.branding_label.setText(
                f"Key: {self.branding.project_key}, "
                f"Prefix: {self.branding.project_prefix} "
                f"Class: {self.branding.bootstrap_class}"
            )
        else:
            self.branding = None
            self.branding_label.setText("Key: ?, Prefix: ?, Class: ?Bootstrap")

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
            if resp == QMessageBox.Cancel:
                return

        template_name = self.template_combo.currentText()
        structure = self._get_template_structure(template_name)

        extras = {
            "readme": self.chk_readme.isChecked(),
            "gitignore": self.chk_gitignore.isChecked(),
            "init_git": self.chk_init_git.isChecked(),
            "venv": self.chk_venv.isChecked(),
            "open_after": self.chk_open_after.isChecked(),
            "copy_connector": self.chk_copy_connector.isChecked(),
            "branding_doc": self.chk_branding_doc.isChecked(),
        }

        self.create_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

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

        if self.selected_directory:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor = self.db_connection.cursor()
            cursor.execute('INSERT INTO logs (directory, user, timestamp, path) VALUES (?, ?, ?, ?)',
                           (self.project_name_input.text().strip(), self.user_system_name, timestamp, self.selected_directory))
            self.db_connection.commit()

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
        """
        Updated template structure based on NileAndSinaiV2 and NexPlacify patterns.

        Key Changes:
        - Resources/ folder removed (now using Modules/)
        - API endpoints organized under Api/V1/ (versioned)
        - Proper separation: Website (public), Accounts (user), Admins (admin)
        - Services/ for business logic
        - Modules/ for reusable components (nav, footer, etc.)
        """
        default = {
            'Assets': {
                # Website (Public-facing site)
                'Website': {
                    'Contents': {
                        'Landing': {},  # Landing page sections
                        'Pages': {},    # Page-specific components
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

                # Accounts (User authentication & profile)
                'Accounts': {
                    'Contents': {
                        'Auth': {},      # Login/register components
                        'Profile': {},   # Profile page components
                        'Dashboard': {}, # Dashboard components
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

                # Admins (Admin panel)
                'Admins': {
                    'Contents': {
                        'Dashboard': {},  # Admin dashboard components
                        'Analytics': {},  # Analytics components
                        'Management': {}, # Management components
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

                # Services (Business logic layer)
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

                # Modules (Reusable components - replaces Resources)
                'Modules': {
                    'nav.php': None,
                    'footer.php': None,
                    'seo.php': None,
                    'base.css': None,
                    'shared-scripts.js': None,
                },

                # Extras (Documentation, SQL, Updates)
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

                # Miscellaneous (Testing, context, etc.)
                'Miscellaneous': {
                    'Context': {},
                    'Information': {},
                    'Testing': {},
                },
            },

            # Root-level files
            'index.php': None,
            '.env': None,
            '.env.example': None,
            'composer.json': None,
            'composer.lock': None,
            '.gitignore': None,
            '.htaccess': None,
        }

        # Microservice template (for API-only projects)
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

# ---------- Run ----------
def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    w = ModernDirectoryCreator()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
