# AutoMatic File Generator

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![Status](https://img.shields.io/badge/status-Active-success.svg)
![Version](https://img.shields.io/badge/version-2.0.0-orange.svg)

**A professional, GUI-based project structure generator with intelligent Connector framework branding**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

![Screenshot](https://via.placeholder.com/800x500/0f1417/4b8cff?text=AutoMatic+File+Generator+UI)

</div>

---

## Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Connector Branding System](#-connector-branding-system)
- [Templates](#-templates)
- [Usage Guide](#-usage-guide)
- [Configuration](#-configuration)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)
- [Credits](#-credits)

---

##  Overview

**AutoMatic File Generator** is a sophisticated PyQt5-based GUI tool that automates the creation of professional PHP project structures with:

- ✅ **Intelligent Branding System** - Automatically generates and injects project-specific prefixes throughout your codebase
- ✅ **Pre-built Connector Framework** - Production-ready infrastructure layer (Auth, Database, Security, Logger, Services)
- ✅ **Multiple Templates** - Website, Microservice, and API templates out of the box
- ✅ **Real-time Preview** - See your project branding (key, prefix, class names) as you type
- ✅ **Git Integration** - Automatic git initialization and .gitignore generation
- ✅ **SQLite Logging** - Full audit trail of all created projects
- ✅ **Cross-platform** - Works on Windows, Linux, and macOS

### Why Use This?

Traditional project generators create generic structures. **AutoMatic File Generator** goes further by:

1. **Branding Your Infrastructure** - Every function, class, and constant is automatically prefixed with your project name
2. **Preventing Naming Collisions** - Multiple projects can coexist without conflicts
3. **Enforcing Best Practices** - Follows proven architectural patterns from production systems
4. **Saving Hours of Setup** - What takes hours manually is done in seconds

---

##  Features

###  Modern GUI Interface
- **Dark-themed** professional UI with hover effects and animations
- **Real-time branding preview** showing generated keys and prefixes
- **Progress tracking** with detailed activity logs
- **Background processing** with cancellation support

###  Intelligent Branding System
```
Project Name: "NileAndSinai"
↓
Auto-generates:
  • Key: NSA
  • Prefix: nsa_
  • Bootstrap Class: NileAndSinaiBootstrap
  • Version Constant: NSA_BOOTSTRAP_VERSION
```

All Connector files automatically updated with your project branding!

###  Pre-built Architecture
- **Connector Layer** (Infrastructure)
  - Authentication (JWT, Session, Token, Permissions)
  - Database (PDO, Query Builder, Connection Pool)
  - Security (CSRF, Headers, Rate Limiting, Origin Validation)
  - Logger (Structured event logging)
  - Services (Cache, Config, Health, Exception Handler)
  - Helpers (Response, Sanitizer, Validator, Utilities)
  - Exceptions (Custom typed exceptions)

- **Application Layers**
  - Website (Public site with Contents/Pages/Api/V1 structure)
  - Accounts (User authentication and profile management)
  - Admins (Admin panel with dashboard and analytics)
  - Services (Business logic layer)
  - Modules (Reusable components: nav, footer, SEO)

###  Template System
- **Default Website Template** - Full-featured web application structure
- **Microservice Template** - API-first microservice architecture
- **Extensible** - Easy to add custom templates

###  Project Management
- **Git Integration** - Auto-initialize repositories
- **Virtual Environment** - Create Python venv placeholders
- **Documentation** - Auto-generate README and branding context docs
- **Export Logs** - CSV export of all project creation history

---

##  Installation

### Prerequisites

- Python 3.8 or higher
- PyQt5

### Step 1: Clone Repository

```bash
git clone https://github.com/BOSS294/AutoMatic-File-Generator.git
cd AutoMatic-File-Generator
```

### Step 2: Install Dependencies

```bash
pip install PyQt5
```

Or use requirements.txt (if provided):

```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
python directory_creator.py
```

The GUI should launch successfully.

---

##  Quick Start

### 1. Launch the Application

```bash
python directory_creator.py
```

### 2. Create Your First Project

1. **Enter Project Name**: Type your project name (e.g., "MyAwesomeProject")
   - Watch the branding preview update in real-time
   - Key: `MAP`, Prefix: `map_`, Class: `MyAwesomeProjectBootstrap`

2. **Select Parent Directory**: Choose where to create your project

3. **Choose Template**: Select "Default Website Template" or "Microservice"

4. **Configure Options**:
   - ✅ Create README.md
   - ✅ Create .gitignore
   - ✅ Copy & inject Connector layer
   - ✅ Create branding context documentation
   - ☐ Init git repository
   - ☐ Create virtual environment
   - ☐ Open folder after creation

5. **Click "Create Structure"**

6. **Done!** Your project is ready with:
   - Fully branded Connector layer
   - Complete directory structure
   - Documentation files
   - Version-controlled API structure

### 3. Verify Branding

Navigate to your project and check:

```bash
cd path/to/MyAwesomeProject/Assets/Connector

# Check function prefix
grep -r "function map_" .

# Check bootstrap class
grep -r "class MyAwesomeProjectBootstrap" .

# Verify no old branding remains
grep -r "NileAndSinai\|nsa_" . # Should be empty
```

---

##  Project Structure

### Generated Structure

```
MyAwesomeProject/
├── Assets/
│   ├── Connector/                    # Branded infrastructure layer
│   │   ├── _bootstrap.php            # Entry point (map_bootstrap, map_db, map_config)
│   │   ├── connector.php             # Core environment & security
│   │   ├── Auth/                     # JWT, Session, Token, Permissions
│   │   ├── Database/                 # PDO, QueryBuilder, ConnectionPool
│   │   ├── Security/                 # CSRF, Headers, RateLimiter, OriginValidator
│   │   ├── Logger/                   # Structured event logging
│   │   ├── Services/                 # Cache, Config, Health, ApiExceptionHandler
│   │   ├── Helpers/                  # Response, Sanitizer, Validator, Utilities
│   │   └── Exceptions/               # Custom exception hierarchy
│   │
│   ├── Website/                      # Public site
│   │   ├── Contents/
│   │   │   ├── Landing/              # Landing page components
│   │   │   └── Pages/                # Page-specific components
│   │   ├── Pages/                    # Rendered pages (index, about, contact, etc.)
│   │   ├── Api/V1/Pages/             # API endpoints (versioned)
│   │   ├── Images/
│   │   ├── Scripts/
│   │   ├── Styles/
│   │   └── Videos/
│   │
│   ├── Accounts/                     # User authentication & profiles
│   │   ├── Contents/                 # Auth, Profile, Dashboard components
│   │   ├── Pages/                    # Login, register, dashboard, profile
│   │   ├── Api/V1/                   # Versioned API structure
│   │   │   ├── Auth/                 # login.php, register.php, logout.php, me.php
│   │   │   ├── Profile/              # overview.php, update.php, picture.php
│   │   │   ├── Dashboard/            # overview.php
│   │   │   └── Settings/             # overview.php, update.php, password.php
│   │   ├── Scripts/
│   │   └── Styles/
│   │
│   ├── Admins/                       # Admin panel
│   │   ├── Contents/                 # Dashboard, Analytics, Management components
│   │   ├── Pages/                    # Admin pages
│   │   ├── Api/V1/                   # Admin API endpoints
│   │   │   ├── Auth/                 # Admin authentication
│   │   │   ├── Dashboard/            # stats.php, overview.php
│   │   │   └── Users/                # list.php, get.php, update.php
│   │   ├── Scripts/
│   │   └── Styles/
│   │
│   ├── Services/                     # Business logic layer
│   │   ├── Accounts/
│   │   ├── Auth/
│   │   ├── Products/
│   │   └── Email/
│   │
│   ├── Modules/                      # Reusable components
│   │   ├── nav.php                   # Site navigation
│   │   ├── footer.php                # Site footer
│   │   ├── seo.php                   # SEO meta rendering
│   │   ├── base.css                  # Shared styles
│   │   └── shared-scripts.js         # Common JavaScript
│   │
│   ├── Extras/
│   │   ├── Documentations/           # Project docs
│   │   ├── Sqls/                     # Database schemas & migrations
│   │   ├── Updates/                  # Changelogs
│   │   └── Connections/              # External service connections
│   │
│   └── Miscellaneous/
│       ├── Context/
│       ├── Information/
│       └── Testing/
│
├── index.php                         # Entry point
├── .env                              # Environment configuration
├── .env.example                      # Environment template
├── composer.json                     # Composer dependencies
├── composer.lock
├── .gitignore                        # Git ignore rules
├── .htaccess                         # Apache configuration
├── README.md                         # Project README
└── CONNECTOR_BRANDING_CONTEXT.md    # Branding reference (auto-generated)
```

---

##  Connector Branding System

### How It Works

The branding system ensures every project has unique identifiers throughout its codebase.

#### Pattern Extraction

```python
"NileAndSinai" → NSA (capital letters)
"NexPlacify"   → NXP (capital letters)
"MyProject"    → MP  (first 3 letters if < 2 capitals)
```

#### Replacement Patterns

1. **File Headers**
   ```php
   /**
    * MyProject V2 - CSRF Protection
    * Version: 2.0.0
    */
   ```

2. **Version Constants**
   ```php
   const MP_BOOTSTRAP_VERSION = '2.0.0';
   ```

3. **Bootstrap Classes**
   ```php
   final class MyProjectBootstrap {
       public static function load(): void { ... }
       public static function boot(array $options = []): array { ... }
   }
   ```

4. **Global Functions**
   ```php
   function mp_bootstrap(array $options = []): array { ... }
   function mp_db(): PDO { ... }
   function mp_config(string $key, mixed $default = null): mixed { ... }
   function mp_log_error(string $message): void { ... }
   ```

5. **Session Keys**
   ```php
   private const SESSION_KEY = '_mp_csrf_token';
   private const FINGERPRINT_KEY = '_mp_fingerprint';
   ```

6. **Error Messages**
   ```
   [MyProject Logger Failure] Database connection lost
   [MyProject Blocker Logger Failure] Rate limit exceeded
   ```

7. **Copyright Headers**
   ```php
   /**
    * MyProject and associated branding are project marks where applicable.
    * All rights reserved.
    */
   ```

### Branding Context Documentation

Every project gets a `CONNECTOR_BRANDING_CONTEXT.md` with:
- Quick reference of all branded functions
- Usage examples
- Session key mappings
- Validation commands
- Guidelines for future AI

---

## Templates

### 1. Default Website Template

Full-featured web application with:
- Public website (landing, pages, contact)
- User accounts (auth, profile, dashboard)
- Admin panel (dashboard, analytics, user management)
- Service layer for business logic
- Modular components for reusability
- API versioning (V1)

**Best for:**
- E-commerce platforms
- SaaS applications
- Content management systems
- Community platforms

### 2. Microservice Template

API-first architecture with:
- Versioned API structure (V1)
- Controllers and middleware
- Service layer
- Database models
- Docker support
- Testing structure

**Best for:**
- RESTful APIs
- Backend services
- Microservice architectures
- Mobile app backends

### 3. Custom Templates

Create your own template by modifying `_get_template_structure()` in `directory_creator.py`.

---

##  Usage Guide

### Basic Usage

```python
from directory_creator import ProjectBranding

# Generate branding for your project
branding = ProjectBranding("MyAwesomeProject")
print(branding.project_key)        # "MAP"
print(branding.project_prefix)     # "map_"
print(branding.bootstrap_class)    # "MyAwesomeProjectBootstrap"
```

### API Endpoint Example

After generating your project, create API endpoints like this:

```php
<?php
declare(strict_types=1);

require_once dirname(__DIR__, 4) . '/Connector/_bootstrap.php';

map_bootstrap([
    'security' => true,
    'session' => true,
    'methods' => ['GET', 'POST'],
    'json' => true,
]);

// Authenticate
$userId = $_SESSION['user_id'] ?? null;
if (!$userId) {
    map_json_response(['success' => false, 'message' => 'Unauthorized'], 401);
}

// Validate CSRF for state-changing operations
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    $csrf = $_POST['csrf_token'] ?? $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '';
    if (!map_validate_csrf($csrf)) {
        map_json_response(['success' => false, 'message' => 'CSRF failed'], 403);
    }
}

// Process request
try {
    $pdo = map_db();
    // Your business logic here
    
    map_json_response(['success' => true, 'data' => $result]);
} catch (Exception $e) {
    map_log_error($e->getMessage());
    map_json_response(['success' => false, 'message' => 'Server error'], 500);
}
```

### Verifying Branding

After project creation, verify everything was branded correctly:

```bash
cd path/to/MyAwesomeProject/Assets/Connector

# Check all functions have correct prefix
grep -r "function map_" . | wc -l  # Should return multiple results

# Check bootstrap class
grep -r "class MyAwesomeProjectBootstrap" .

# Verify no old branding remains
grep -r "nsa_\|NSA\|NileAndSinai" .  # Should return NOTHING

# Check session keys
grep -r "_map_" .
```

---

##  Configuration

### Environment Variables

The generated `.env` file includes:

```env
# Application
APP_ENV=development
APP_DEBUG=true
APP_URL=http://localhost

# Database
DB_DRIVER=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=database_name
DB_USER=root
DB_PASSWORD=
DB_CHARSET=utf8mb4

# Security
JWT_SECRET=your-secret-key-here
ALLOWED_ORIGINS=http://localhost,https://yourdomain.com

# Session
SESSION_LIFETIME=7200
SESSION_SECURE=false
SESSION_HTTP_ONLY=true
```

### Connector Bootstrap Options

```php
map_bootstrap([
    'security' => true,      // Apply security headers
    'csp' => true,          // Content Security Policy
    'session' => true,      // Start session management
    'csrf' => true,         // Enable CSRF protection
    'json' => true,         // Set JSON content type
    'methods' => ['GET', 'POST'],  // Allowed HTTP methods
    'payload_limit' => 10,  // Max payload size (MB)
    'rate_limit' => [       // Rate limiting config
        'enabled' => true,
        'requests' => 60,
        'window' => 60,
    ],
    'exception_handler' => true,  // Centralized exception handling
]);
```

---

## 📚 Documentation

### Core Documentation Files

1. **CONNECTOR_BRANDING_GUIDE.md** - Comprehensive branding system reference
2. **CONNECTOR_BRANDING_CONTEXT.md** - Per-project branding reference (auto-generated)
3. **COMMON_IMPLEMENTATIONS_ANALYSIS.md** - Architectural patterns and conventions

### Additional Resources

- [Central Project Engineering Playbook](CENTRAL_PROJECT_ENGINEERING_PLAYBOOK.md) - Best practices and standards
- [Common Implementations Analysis](COMMON_IMPLEMENTATIONS_ANALYSIS.md) - Pattern analysis
- [Interactive Pattern Browser](project-patterns-interactive.html) - Visual reference

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Reporting Issues

1. Check existing issues first
2. Provide detailed description
3. Include steps to reproduce
4. Attach screenshots if relevant

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/BOSS294/AutoMatic-File-Generator.git
cd AutoMatic-File-Generator
pip install -r requirements.txt
python directory_creator.py
```

### Code Style

- Follow PEP 8 for Python code
- Use type hints where applicable
- Add docstrings to functions and classes
- Keep functions focused and single-purpose

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 Mayank Chawdhari (BOSS294) / Privonix Technologies

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR DEALINGS IN THE
SOFTWARE.
```

---

## 👏 Credits

### Author

**Mayank Chawdhari** (aka BOSS294)  
Organization: Privonix Technologies

### Acknowledgments

- Inspired by production architectures from NileAndSinaiV2 and NexPlacify projects
- Built with PyQt5 for cross-platform GUI
- Connector framework design based on proven PHP 8+ patterns

### Technologies Used

- Python 3.8+
- PyQt5 for GUI
- SQLite for logging
- Git for version control

---

## 🔗 Links

- **Repository**: [https://github.com/BOSS294/AutoMatic-File-Generator](https://github.com/BOSS294/AutoMatic-File-Generator)
- **Issues**: [https://github.com/BOSS294/AutoMatic-File-Generator/issues](https://github.com/BOSS294/AutoMatic-File-Generator/issues)
- **Discussions**: [https://github.com/BOSS294/AutoMatic-File-Generator/discussions](https://github.com/BOSS294/AutoMatic-File-Generator/discussions)

---

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/BOSS294/AutoMatic-File-Generator?style=social)
![GitHub forks](https://img.shields.io/github/forks/BOSS294/AutoMatic-File-Generator?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/BOSS294/AutoMatic-File-Generator?style=social)

---

<div align="center">

**Made with ❤️ by Mayank Chawdhari**

If this project helped you, please consider giving it a ⭐!

[⬆ Back to Top](#-automatic-file-generator)

</div>
