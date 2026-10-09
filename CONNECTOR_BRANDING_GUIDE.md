# Connector Branding & Project Prefix System

**Last Updated:** 2026-10-09  
**Version:** 1.0.0  
**For:** Future AI & Development Teams

---

## Overview

The Connector layer is a **pre-existing, reusable infrastructure** that comes with every new project. When a new project is created, the Connector files are automatically customized with **project-specific branding** and **prefixes** to maintain trademark consistency and avoid naming collisions.

## Branding Pattern

### Components of Project Branding

Every project generates **three key identifiers**:

| Component | Example (NileAndSinai) | Example (NexPlacify) | Format |
|-----------|---|---|---|
| **Project Name** | `NileAndSinai` | `NexPlacify` | PascalCase full name |
| **Project Key** | `NSA` | `NXP` | 3-letter uppercase acronym |
| **Function Prefix** | `nsa_` | `nxp_` | Lowercase key + underscore |
| **Bootstrap Class** | `NileAndSinaiBootstrap` | `NexPlacifyBootstrap` | ProjectName + "Bootstrap" |
| **Version Constant** | `NSA_BOOTSTRAP_VERSION` | `NXP_BOOTSTRAP_VERSION` | Key + "_BOOTSTRAP_VERSION" |

### Key Generation Rules

**From project name:** `MyProjectName`

1. **Project Key**: First letter of each word, uppercase (e.g., `MPN`)
2. **Function Prefix**: Lowercase key + `_` (e.g., `mpn_`)
3. **Bootstrap Class**: `{ProjectName}Bootstrap` (e.g., `MyProjectNameBootstrap`)
4. **Version Constant**: `{KEY}_BOOTSTRAP_VERSION` (e.g., `MPN_BOOTSTRAP_VERSION`)

---

## Files & Replacement Patterns

### Pattern: File Headers

**Location:** Every Connector PHP file  
**Format:**
```php
/**
 * {PROJECT_NAME} - {COMPONENT_DESCRIPTION}
 * Version: X.X.X
 * ...
 */
```

**Example (NileAndSinai):**
```php
/**
 * NileAndSinai V2 - Origin Validator
 * Version: 2.0.0
 */
```

**Replacement Template:**
```php
/**
 * {PROJECT_NAME} V2 - {COMPONENT_DESCRIPTION}
 * Version: 2.0.0
 */
```

---

### Pattern: Version Constants

**Location:** `_bootstrap.php`  
**Format:**
```php
const {KEY}_BOOTSTRAP_VERSION = '2.0.0';
```

**Example (NileAndSinai):**
```php
const NSA_BOOTSTRAP_VERSION = '2.0.0';
```

**Rule:** Extracted from `_bootstrap.php` for each project. Never change the version number itself during injection—only the constant name.

---

### Pattern: Bootstrap Class

**Location:** `_bootstrap.php`  
**Format:**
```php
final class {PROJECT_NAME}Bootstrap { ... }
```

**Examples:**
- `NileAndSinaiBootstrap`
- `NexPlacifyBootstrap`
- `MyProjectNameBootstrap`

**All references must be updated:**
- Class definition: `final class {PROJECT_NAME}Bootstrap`
- Static calls: `{PROJECT_NAME}Bootstrap::load()`
- Initialization: `{PROJECT_NAME}Bootstrap::boot($options)`

---

### Pattern: Global Helper Functions

**Location:** `_bootstrap.php` (end of file)  
**Format:**
```php
function {PREFIX}_bootstrap(array $options = []): array { ... }
function {PREFIX}_db(): PDO { ... }
function {PREFIX}_config(string $key, mixed $default = null): mixed { ... }
function {PREFIX}_log_error(string $message): void { ... }
```

**Examples (NileAndSinai):**
```php
function nsa_bootstrap(array $options = []): array
function nsa_db(): PDO
function nsa_config(string $key, mixed $default = null): mixed
function nsa_log_error(string $message): void
```

**Coverage:** Every function prefixed with `{PREFIX}_`

---

### Pattern: Session & Cookie Keys

**Location:** Security/Csrf.php, Auth/Session.php, etc.  
**Format:**
```php
private const SESSION_KEY = '_{PREFIX}_csrf_token';
private const FINGERPRINT_KEY = '_{PREFIX}_fingerprint';
```

**Examples:**
```php
private const SESSION_KEY = '_nsa_csrf_token';
private const FINGERPRINT_KEY = '_nsa_fingerprint';
```

---

### Pattern: Error Messages & Logging

**Location:** Logger/oLogger.php, throughout exception handling  
**Format:**
```
'[{PROJECT_NAME} Logger Failure] ...'
'[{PROJECT_NAME} Blocker Logger Failure] ...'
```

**Examples:**
```
'[NileAndSinai Logger Failure] Could not write to database'
'[NexPlacify Blocker Logger Failure] Rate limit exceeded'
```

---

### Pattern: Copyright & Attribution

**Location:** _bootstrap.php (top of file)  
**Format:**
```php
/**
 * ============================================================================
 * {PROJECT_NAME} V2 - Connector Bootstrap
 * ============================================================================
 *
 * Version      : 2.0.0
 * Connector    : 1.0.1+
 * Project      : {PROJECT_NAME} V2
 *
 * Created by   : Mayank Chawdhari aka BOSS294
 * Organization : Privonix Technologies
 *
 * Copyright / Trademark
 * ---------------------
 * © 2026 Mayank Chawdhari / Privonix Technologies.
 * {PROJECT_NAME} and associated branding are project marks where applicable.
 * All rights reserved.
 * ============================================================================
 */
```

---

## Connector Files & Their Patterns

### Core Files (Always Present)

| File | Patterns to Replace |
|------|---|
| `_bootstrap.php` | Class name, constants, functions, copyright, header |
| `connector.php` | Header comment, class references |
| `Auth/Session.php` | Header, session key constants, function calls |
| `Auth/Jwt.php` | Header, error messages |
| `Auth/Token.php` | Header, session key constants |
| `Auth/Permissions.php` | Header |
| `Database/Database.php` | Header, logging calls |
| `Database/QueryBuilder.php` | Header, logging calls |
| `Database/ConnectionPool.php` | Header |
| `Security/Csrf.php` | Header, session keys, error messages |
| `Security/Headers.php` | Header, error messages |
| `Security/OriginValidator.php` | Header, environment checks |
| `Security/RateLimiter.php` | Header, error messages, logging |
| `Security/DeviceFingerprint.php` | Header, session keys |
| `Security/RequestValidator.php` | Header |
| `Security/RequestContext.php` | Header, constants |
| `Security/Security.php` | Header, function calls |
| `Logger/oLogger.php` | Header, error message format |
| `Logger/LogTypes.php` | Header |
| `Helpers/Response.php` | Header |
| `Helpers/Sanitizer.php` | Header |
| `Helpers/Validator.php` | Header |
| `Helpers/Utilities.php` | Header |
| `Services/CacheService.php` | Header |
| `Services/ConfigService.php` | Header |
| `Services/HealthService.php` | Header |
| `Services/ApiExceptionHandler.php` | Header, error messages |
| `Exceptions/*.php` | Header |

---

## Implementation in directory_creator.py

### Step 1: Extract Project Branding

```python
def extract_project_branding(project_name: str) -> dict:
    """
    Convert project name to branding components.
    
    Example:
        "NileAndSinai" -> {
            "projectName": "NileAndSinai",
            "projectKey": "NSA",
            "projectPrefix": "nsa_",
            "bootstrapClass": "NileAndSinaiBootstrap",
            "versionConstant": "NSA_BOOTSTRAP_VERSION"
        }
    """
    # Extract capital letters for key
    key = ''.join([c for c in project_name if c.isupper()])
    if len(key) < 2:
        key = project_name[:3].upper()
    
    return {
        "projectName": project_name,
        "projectKey": key,
        "projectPrefix": key.lower() + "_",
        "bootstrapClass": project_name + "Bootstrap",
        "versionConstant": key + "_BOOTSTRAP_VERSION",
    }
```

### Step 2: Inject Branding into Connector Files

```python
def inject_connector_branding(connector_path: str, branding: dict) -> None:
    """
    Recursively replace all branding patterns in Connector files.
    """
    replacements = {
        "NileAndSinai": branding["projectName"],
        "NSA": branding["projectKey"],
        "nsa_": branding["projectPrefix"],
        "NileAndSinaiBootstrap": branding["bootstrapClass"],
        "NSA_BOOTSTRAP_VERSION": branding["versionConstant"],
        "_nsa_": "_" + branding["projectPrefix"],
        "[NileAndSinai": "[" + branding["projectName"],
    }
    
    for root, dirs, files in os.walk(connector_path):
        for file in files:
            if file.endswith('.php'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for old, new in replacements.items():
                    content = content.replace(old, new)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
```

---

## Documentation Structure

For every new project, generate a `CONNECTOR_BRANDING_CONTEXT.md` file:

```markdown
# {PROJECT_NAME} - Connector Branding Context

**Project Name:** {PROJECT_NAME}  
**Project Key:** {KEY}  
**Function Prefix:** {PREFIX}  
**Bootstrap Class:** {CLASS}  
**Created:** {DATE}

## Quick Reference

All global functions start with `{PREFIX}_`:
- `{PREFIX}_bootstrap()` - Initialize Connector
- `{PREFIX}_db()` - Get PDO instance
- `{PREFIX}_config()` - Get configuration
- `{PREFIX}_log_error()` - Log errors

## File Header Pattern

Every Connector file has:
```php
/**
 * {PROJECT_NAME} - {COMPONENT}
 * Version: 2.0.0
 */
```

## Session Keys

- CSRF Token: `_{PREFIX}_csrf_token`
- Fingerprint: `_{PREFIX}_fingerprint`

## Bootstrap Class

All Connector initialization goes through:
```php
final class {CLASS} { ... }
```

## Version Constant

The Connector version for this project:
```php
const {VERSION_CONSTANT} = '2.0.0';
```

---

For AI reviewing this project later: The Connector branding is **not arbitrary**. It:
1. Prevents naming collisions in shared environments
2. Makes it instantly clear which project a function belongs to
3. Maintains trademark consistency
4. Allows multiple projects to coexist in the same codebase

All replacements follow the patterns documented in `CONNECTOR_BRANDING_GUIDE.md`.
```

---

## Testing Branding Injection

After creating a new project with Connector, verify:

```bash
# Check all function prefixes are correct
grep -r "function {PREFIX}_" Assets/Connector/

# Check bootstrap class name
grep -r "final class {CLASS}" Assets/Connector/

# Check version constant
grep -r "const {VERSION_CONSTANT}" Assets/Connector/

# Check no NileAndSinai or NSA remain
grep -r "NileAndSinai\|NSA" Assets/Connector/ # Should return EMPTY
```

---

## Common Issues & Resolutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Functions still have `nsa_` prefix | Injection script failed | Re-run branding injection with correct path |
| Bootstrap class name is wrong | Project name parsing error | Verify project name capitalization |
| Session keys still have `_nsa_` | Partial injection | Check all .php files in Connector/ |
| Version constant unchanged | Expected behavior | Version constants should NOT be changed, only the key prefix |

---

## Future Enhancements

- [ ] Automate branding audit tool
- [ ] Generate branding summary report after project creation
- [ ] Support for multi-project environments
- [ ] Branding validator (ensure no cross-project prefixes)

---

**Document Version:** 1.0.0  
**Last Reviewed:** 2026-10-09  
**For Questions:** See directory_creator.py implementation notes

