# Common Implementations Across NileAndSinaiV2 & NexPlacify

**Analysis Date:** 2026-10-09  
**Based On:** Direct project inspection + Central Project Engineering Playbook  
**Purpose:** Document shared patterns for standardized development

---

## 1. SHARED DIRECTORY STRUCTURE

Both projects follow the same **canonical modular layout**:

```
project-root/
├── index.php                          # Front controller
├── composer.json & composer.lock
├── .gitignore
├── .env (not tracked)
├── .env.example
│
├── Assets/
│   ├── Connector/                     # ✅ IDENTICAL in both
│   │   ├── _bootstrap.php             # Entry point for all APIs
│   │   ├── connector.php              # Low-level env/security/db
│   │   ├── Auth/                      # Session, JWT, Token, Permissions
│   │   ├── Database/                  # PDO connection, QueryBuilder
│   │   ├── Security/                  # CSRF, Headers, OriginValidator, RateLimiter
│   │   ├── Logger/                    # Structured event logging
│   │   ├── Helpers/                   # Response, Sanitizer, Validator, Utilities
│   │   ├── Services/                  # Cache, Config, Health, ApiExceptionHandler
│   │   ├── Exceptions/                # Auth, Authorization, Validation, RateLimit, Security
│   │   └── README.md
│   │
│   ├── Website/                       # ✅ SIMILAR STRUCTURE
│   │   ├── Contents/                  # Modular page components
│   │   │   ├── Landing/               # Hero, sections (NS-*, NX-*)
│   │   │   └── Pages/                 # Specific pages
│   │   ├── Pages/                     # Rendered final pages
│   │   └── Api/                       # REST endpoints
│   │       ├── Products/ (Nile)
│   │       ├── Pages/ (Nile)
│   │       ├── V1/ (NexPlacify)
│   │       │   ├── Accounts/
│   │       │   ├── Jobs/
│   │       │   └── Admin/
│   │       └── _bootstrap.php
│   │
│   ├── Accounts/                      # ✅ DIFFERENT IN NEX (more extensive)
│   │   ├── Contents/                  # Auth pages, Onboarding, Resume, Profile
│   │   └── ...
│   │
│   ├── Admins/ (NexPlacify)           # ⚠️ Nile doesn't have explicit admin
│   │   ├── Pages/
│   │   ├── Contents/
│   │   ├── Api/
│   │   └── Services/
│   │
│   ├── Modules/                       # ✅ IDENTICAL
│   │   ├── nav.php
│   │   ├── footer.php
│   │   ├── base.css
│   │   └── shared-scripts.js
│   │
│   ├── Services/                      # ✅ IDENTICAL PATTERN
│   │   ├── Accounts/
│   │   ├── Profile/
│   │   ├── Resume/
│   │   ├── AI/
│   │   └── ...
│   │
│   └── Extras/
│       ├── Documentations/
│       ├── Sqls/                      # Migrations & schema
│       └── Updates/                   # Changelogs
│
├── vendor/                             # Composer dependencies
└── composer.lock
```

### Key Points:
- **Connector/ is IDENTICAL** in both projects
- **Website structure is SIMILAR** with semantic naming (NS-*/NX-* for sections)
- **Services/ follows SAME PATTERN** (Accounts, Profile, Resume, etc.)
- **NexPlacify adds** formal Admin/ and expanded Accounts/
- **Nile is simpler** (less account management, no scraping pipeline)

---

## 2. CONNECTOR LAYER (Identical in Both)

### 2.1 Low-Level Base Classes

Both projects inherit:

```
Connector/
├── connector.php
│   ├── class OTAEnv              # Environment variable loading
│   ├── class OTASecurity         # Security headers, HTTPS checks, origin validation
│   └── class OTADatabase         # PDO connection, health checks
│
├── Auth/
│   ├── Session.php               # Session start, get/set, destroy
│   ├── Jwt.php                   # JWT encode/decode with expiry
│   ├── Token.php                 # Opaque token generation & verification
│   └── Permissions.php           # Role-based access control (NexPlacify extends this)
│
├── Database/
│   ├── ConnectionPool.php        # Connection pooling
│   ├── Database.php              # PDO wrapper facade
│   └── QueryBuilder.php          # Fluent query building
│
├── Security/
│   ├── Headers.php               # Response security headers
│   ├── OriginValidator.php       # CORS/allowed origins check
│   ├── Csrf.php                  # Token generation & validation
│   ├── RateLimiter.php           # Request rate limiting
│   ├── RequestValidator.php      # Method, payload size, content-type
│   ├── RequestContext.php        # Request ID generation & tracking
│   └── DeviceFingerprint.php     # Device risk signals
│
├── Helpers/
│   ├── Response.php              # JSON response formatting
│   ├── Sanitizer.php             # Text/email/filename sanitization
│   ├── Validator.php             # required/email/integer/uuid validation
│   └── Utilities.php             # Common utilities
│
├── Services/
│   ├── ConfigService.php         # Configuration access
│   ├── CacheService.php          # File-based TTL caching
│   ├── HealthService.php         # DB health checks
│   └── ApiExceptionHandler.php   # Centralized error handling
│
├── Logger/
│   ├── oLogger.php               # Structured event logging
│   ├── LogTypes.php              # Log type constants
│   └── create_tables.sql         # Logger schema
│
└── Exceptions/
    ├── AuthenticationException.php
    ├── AuthorizationException.php
    ├── ValidationException.php
    ├── RateLimitException.php
    └── SecurityException.php
```

### 2.2 Bootstrap Entry Point (_bootstrap.php)

Both projects use **identical bootstrap pattern**:

```php
<?php
declare(strict_types=1);

require_once dirname(__DIR__, 3) . '/Connector/_bootstrap.php';

// Bootstrap with options
nsa_bootstrap([
    'security'       => true,      // Apply security headers
    'csp'            => true,      // Content Security Policy
    'session'        => true,      // Start PHP session
    'csrf'           => true,      // Require CSRF token
    'json'           => true,      // Require JSON content-type
    'methods'        => ['GET', 'POST'],
    'payload_limit'  => 1024 * 1024,
    'rate_limit'     => null,      // Set for sensitive endpoints
]);

$pdo = nsa_db();
$userId = $_SESSION['user_id'] ?? null;
```

### 2.3 Helper Functions Exposed

Both projects use these identical helpers:

| Function | Purpose |
|----------|---------|
| `nsa_bootstrap(options)` | Initialize Connector with security/auth/validation |
| `nsa_db()` | Get shared PDO connection |
| `nsa_config(key, default)` | Read configuration |
| `nsa_request_id()` | Get request correlation ID |
| `nsa_json_body()` | Decode JSON request body |
| `nsa_rate_limit(key, limit, window)` | Apply rate limiting |
| `nsa_log_event(type, status, message, details)` | Structured logging |
| `nsa_bootstrap_status()` | Diagnostics |

---

## 3. API CREATION PATTERN (Shared Template)

### 3.1 File Organization

Both projects organize endpoints identically:

```
Assets/Website/Api/
├── _bootstrap.php                # Shared API bootstrap
├── V1/ (NexPlacify)
│   ├── Accounts/
│   │   ├── Auth/
│   │   │   ├── login.php
│   │   │   ├── register.php
│   │   │   ├── logout.php
│   │   │   └── google.php
│   │   ├── Profile/
│   │   │   ├── overview.php
│   │   │   ├── update.php
│   │   │   └── picture.php
│   │   ├── Resume/
│   │   │   ├── upload.php
│   │   │   ├── analyze.php
│   │   │   └── overview.php
│   │   └── Readiness/
│   │       ├── overview.php
│   │       ├── generate.php
│   │       └── history.php
│   └── Jobs/
│       ├── list.php
│       ├── skill-gaps.php
│       └── detail.php
│
├── Products/ (NileAndSinai)
│   ├── index.php               # List all products
│   ├── detail.php              # Single product
│   ├── review.php              # Product reviews
│   ├── catalog-options.php     # Filters
│   └── _service.php            # Shared service layer
│
└── Pages/
    ├── contact-engine.php
    ├── faqs-engine.php
    └── request-quote-engine.php
```

### 3.2 Endpoint Template (Copy-Paste Ready)

**NexPlacify Example: `/api/v1/accounts/profile/overview.php`**

```php
<?php
declare(strict_types=1);

require_once dirname(__DIR__, 4) . '/Connector/_bootstrap.php';

// Bootstrap with security settings
nsa_bootstrap([
    'security'      => true,
    'session'       => true,
    'methods'       => ['GET'],
    'json'          => true,
]);

// Authenticate
$userId = $_SESSION['user_id'] ?? null;
if (!$userId) {
    nsa_json_response(['success' => false, 'message' => 'Unauthorized'], 401);
}

// Get database connection
$pdo = nsa_db();

// Call service
$profileService = new ProfileService($pdo);
try {
    $profile = $profileService->overview($userId);
    nsa_json_response([
        'success' => true,
        'data'    => $profile,
        'version' => OTA_CONNECTOR_VERSION,
    ], 200);
} catch (Exception $e) {
    nsa_log_event('profile.overview', 'error', $e->getMessage(), ['user_id' => $userId]);
    nsa_json_response([
        'success'    => false,
        'message'    => 'Failed to fetch profile',
        'request_id' => nsa_request_id(),
    ], 500);
}
```

### 3.3 Common HTTP Methods & Patterns

Both projects use identical HTTP semantics:

```
GET  /api/v1/resource               → List or overview
GET  /api/v1/resource/:id           → Single item detail
POST /api/v1/resource               → Create
POST /api/v1/resource/:id/action    → Perform action
PUT  /api/v1/resource/:id           → Update
DELETE /api/v1/resource/:id         → Delete
```

### 3.4 Response Format (Identical)

Both projects return identical JSON structure:

```json
{
  "success": true,
  "message": "Operation completed",
  "data": {},
  "version": "1.0.0",
  "request_id": "req-abc123"
}
```

**Error response:**

```json
{
  "success": false,
  "message": "Safe error message",
  "data": {
    "request_id": "req-abc123",
    "field_errors": {}
  },
  "version": "1.0.0"
}
```

---

## 4. SERVICE LAYER PATTERN (Shared)

Both projects organize business logic identically:

### 4.1 Service Class Structure

```php
<?php
declare(strict_types=1);

// Location: Assets/Services/Feature/FeatureService.php

final class FeatureService
{
    public function __construct(private PDO $pdo)
    {
    }

    // Overview/read methods
    public function overview(int $userId): array
    {
        // Fetch from database
        $stmt = $this->pdo->prepare(
            'SELECT * FROM feature WHERE user_id = :user_id'
        );
        $stmt->execute([':user_id' => $userId]);
        return $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];
    }

    // Update/write methods
    public function update(int $userId, array $data): bool
    {
        // Validate
        if (!isset($data['name']) || $data['name'] === '') {
            throw new ValidationException('Name is required');
        }

        // Update with transaction
        try {
            $this->pdo->beginTransaction();

            $stmt = $this->pdo->prepare(
                'UPDATE feature SET name = :name WHERE user_id = :user_id'
            );
            $stmt->execute([
                ':name'    => $data['name'],
                ':user_id' => $userId,
            ]);

            $this->pdo->commit();
            return true;
        } catch (Exception $e) {
            $this->pdo->rollBack();
            throw $e;
        }
    }

    // Helper methods
    private function validateData(array $data): void
    {
        if (empty($data['name'])) {
            throw new ValidationException('Name required');
        }
    }
}
```

### 4.2 Services Used in Both Projects

| Service | Location | Purpose |
|---------|----------|---------|
| `ProfileService` | `Assets/Services/Accounts/Profile/` | User profile management |
| `ResumeService` | `Assets/Services/Accounts/Resume/` | Resume upload & analysis (Nex) |
| `AuthService` | `Assets/Services/Accounts/Auth/` | Authentication & authorization |
| `OnboardingService` | `Assets/Services/Accounts/Onboarding/` | User setup workflow (Nex) |
| `ReadinessService` | `Assets/Services/Accounts/Readiness/` | Readiness scoring (Nex) |
| `ProductService` | `Assets/Services/Website/Products/` | Product management (Nile) |

---

## 5. AUTHENTICATION & AUTHORIZATION PATTERNS

### 5.1 Session-Based Auth (Both Use)

```php
// Login endpoint
$email = $_POST['email'] ?? null;
$password = $_POST['password'] ?? null;

// Validate credentials
$stmt = $pdo->prepare('SELECT id, password_hash FROM users WHERE email = :email');
$stmt->execute([':email' => $email]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);

if (!$user || !password_verify($password, $user['password_hash'])) {
    nsa_log_event('auth.login', 'failure', 'Invalid credentials', ['email' => $email]);
    nsa_json_response(['success' => false, 'message' => 'Invalid credentials'], 401);
}

// Regenerate session (security best practice)
Session::regenerate();

// Set session variables
$_SESSION['user_id'] = $user['id'];
$_SESSION['email'] = $user['email'];
$_SESSION['authenticated_at'] = time();

nsa_log_event('auth.login', 'success', 'User logged in', ['user_id' => $user['id']]);
```

### 5.2 JWT Tokens (Both Support)

```php
// Encode JWT
$token = Jwt::encode([
    'user_id' => $userId,
    'email'   => $email,
    'exp'     => time() + 3600,  // 1 hour expiry
]);

// Decode and validate
try {
    $payload = Jwt::decode($token);
    $userId = $payload['user_id'];
} catch (Exception $e) {
    nsa_json_response(['success' => false, 'message' => 'Invalid token'], 401);
}
```

### 5.3 CSRF Protection (Both Enforce)

```php
// In form-rendering code
$csrfToken = Csrf::token();
echo '<input type="hidden" name="csrf_token" value="' . htmlspecialchars($csrfToken) . '">';

// In endpoint with bootstrap
nsa_bootstrap(['csrf' => true, 'session' => true]);

// Token automatically validated if POST/PUT/DELETE
// If invalid: 403 Forbidden
```

### 5.4 Permissions System (Identical)

```php
// Check permission in endpoint
$permissions = new Permissions();

if (!$permissions->can($role, 'admin.view')) {
    nsa_json_response(['success' => false, 'message' => 'Forbidden'], 403);
}

// Permission checking
$allowed = $permissions->canAny($role, ['feature.read', 'feature.admin']);
$allNeeded = $permissions->canAll($role, ['feature.read', 'feature.write']);
```

---

## 6. SECURITY IMPLEMENTATIONS (Identical)

### 6.1 Security Headers Applied

Both projects apply these headers via `OTASecurity`:

```php
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: SAMEORIGIN');
header('Referrer-Policy: strict-origin-when-cross-origin');
header('Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()');
header('Cross-Origin-Opener-Policy: same-origin');
header('Cross-Origin-Resource-Policy: same-origin');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Pragma: no-cache');
header('Expires: 0');

// HTTPS only
if ($isHttps) {
    header('Strict-Transport-Security: max-age=31536000; includeSubDomains; preload');
}
```

### 6.2 Origin Validation

```php
$allowed = OTASecurity::allowedOrigins();  // From config
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';

if (!in_array(rtrim($origin, '/'), $allowed, true)) {
    nsa_json_response(['success' => false, 'message' => 'Origin not allowed'], 403);
}
```

### 6.3 HTTPS Enforcement

```php
// dev/local exemption
$env = strtolower(getenv('APP_ENV') ?: 'production');
if (!in_array($env, ['local', 'development', 'dev'], true)) {
    if (!OTASecurity::isHttps()) {
        throw new RuntimeException('HTTPS is required in production');
    }
}
```

### 6.4 Input Validation

```php
// Using Validator helpers
if (!Validator::email($email)) {
    throw new ValidationException('Invalid email format');
}

if (!Validator::required($name)) {
    throw new ValidationException('Name is required');
}

if (!Validator::integer($userId)) {
    throw new ValidationException('User ID must be integer');
}

if (!Validator::in($status, ['active', 'inactive', 'pending'])) {
    throw new ValidationException('Invalid status');
}
```

### 6.5 Input Sanitization

```php
// Using Sanitizer helpers
$cleanName = Sanitizer::text($_POST['name']);
$cleanEmail = Sanitizer::email($_POST['email']);
$cleanFilename = Sanitizer::filename($_FILES['upload']['name']);
$cleanArray = Sanitizer::array($_POST['items']);
```

### 6.6 Rate Limiting

```php
// Apply rate limit
$result = nsa_rate_limit("login:{$email}", 5, 300);  // 5 attempts per 5 minutes

if (!$result['allowed']) {
    nsa_json_response([
        'success' => false,
        'message' => 'Too many login attempts. Try again later.',
        'retry_after' => $result['retry_after'],
    ], 429);
}
```

### 6.7 Error Handling & Logging

```php
try {
    // Endpoint logic
} catch (AuthenticationException $e) {
    nsa_log_event('endpoint', 'error', $e->getMessage());
    nsa_json_response(['success' => false, 'message' => 'Unauthorized'], 401);
} catch (AuthorizationException $e) {
    nsa_log_event('endpoint', 'error', $e->getMessage());
    nsa_json_response(['success' => false, 'message' => 'Forbidden'], 403);
} catch (ValidationException $e) {
    nsa_json_response(['success' => false, 'message' => $e->getMessage()], 400);
} catch (Exception $e) {
    // Log full details privately
    nsa_log_event('endpoint', 'error', $e->getMessage(), [
        'request_id' => nsa_request_id(),
        'exception'  => get_class($e),
    ]);
    
    // Return safe message to client
    nsa_json_response([
        'success'    => false,
        'message'    => 'An error occurred',
        'request_id' => nsa_request_id(),
    ], 500);
}
```

---

## 7. DATABASE & MIGRATION PATTERNS

### 7.1 Connection Pattern (Identical)

```php
$pdo = nsa_db();  // Get singleton connection

// Use prepared statements ALWAYS
$stmt = $pdo->prepare(
    'SELECT id, name FROM users WHERE email = :email LIMIT 1'
);
$stmt->execute([':email' => $userEmail]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);
```

### 7.2 Schema Files Location

```
Assets/Extras/Sqls/
├── nexplacify_auth_schema_v2.sql
├── nexplacify_oauth_state_schema_v1.sql
├── nexplacify_onboarding_schema_v1.sql
├── profile_workspace_schema-v1.sql
├── resume_intelligence_schema-v2.sql
├── readiness_schema-v3.sql
└── admin_schema-v1.sql
```

### 7.3 Migration Naming Convention

Both use **semantic versioning with date/order**:

```sql
-- File: nexplacify_feature_schema_v1.sql
-- Version: v1
-- Purpose: Initial schema for feature

CREATE TABLE IF NOT EXISTS feature (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 7.4 Transaction Pattern

```php
// For multi-step writes that must succeed together
try {
    $pdo->beginTransaction();

    // Step 1
    $stmt1 = $pdo->prepare('INSERT INTO table1 VALUES (...)');
    $stmt1->execute($data1);

    // Step 2
    $stmt2 = $pdo->prepare('UPDATE table2 SET ... WHERE id = ?');
    $stmt2->execute($data2);

    // All succeed or all fail
    $pdo->commit();

    nsa_log_event('feature', 'success', 'Multi-step operation completed');
} catch (Exception $e) {
    $pdo->rollBack();
    nsa_log_event('feature', 'error', $e->getMessage());
    throw $e;
}
```

---

## 8. PAGE LAYER PATTERN (Both Use)

### 8.1 Thin Wrapper Pattern

```php
<?php
declare(strict_types=1);

// File: Assets/Website/Pages/feature.php

$pageTitle = 'Feature Name';
$activeGroup = 'feature';
$activeItem = 'feature-item';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($pageTitle, ENT_QUOTES, 'UTF-8') ?></title>
    <link rel="stylesheet" href="/Assets/Modules/base.css">
</head>
<body>
    <?php include __DIR__ . '/../Modules/nav.php'; ?>
    
    <main class="content">
        <?php include __DIR__ . '/../Contents/feature/feature-content.php'; ?>
    </main>
    
    <?php include __DIR__ . '/../Modules/footer.php'; ?>
    
    <script src="/Assets/Modules/base.js" defer></script>
</body>
</html>
```

### 8.2 Content Module Pattern

```php
<?php
// File: Assets/Website/Contents/feature/feature-content.php
// This contains the actual feature markup and logic

declare(strict_types=1);

// Get any needed data
$featureId = $_GET['id'] ?? null;
if (!$featureId) {
    echo '<p>Feature not found</p>';
    return;
}

// Fetch data if needed (usually from API via JavaScript)
// But can include PHP-rendered content too

?>
<section class="feature-section">
    <h1><?= htmlspecialchars($featureTitle) ?></h1>
    
    <!-- Content here -->
    
</section>

<style>
    .feature-section { /* Feature-specific styles */ }
</style>

<script>
    // Feature-specific JavaScript
</script>
```

---

## 9. NAMING CONVENTIONS (Shared)

### 9.1 File Naming

| Type | Pattern | Example |
|------|---------|---------|
| Service class | `FeatureService.php` | `ProfileService.php`, `ResumeService.php` |
| API endpoint | `action.php` | `overview.php`, `update.php`, `login.php` |
| Page wrapper | `page-name.php` | `dashboard.php`, `settings.php` |
| Content module | `page-name-content.php` | `dashboard-content.php` |
| Schema migration | `feature_schema_vN.sql` | `auth_schema_v1.sql` |
| Helper/utility | `UtilityName.php` | `Validator.php`, `Sanitizer.php` |

### 9.2 Database Naming

| Type | Pattern | Example |
|------|---------|---------|
| Table | `snake_case` | `user_profiles`, `resume_data` |
| Column | `snake_case` | `user_id`, `created_at`, `is_active` |
| Primary key | `id` | `id INT PRIMARY KEY AUTO_INCREMENT` |
| Foreign key | `{entity}_id` | `user_id`, `profile_id` |
| Timestamp | `{action}_at` | `created_at`, `updated_at`, `verified_at` |

### 9.3 Function/Method Naming

| Type | Pattern | Example |
|------|---------|---------|
| Helper (nsa_*) | `nsa_action()` | `nsa_db()`, `nsa_log_event()` |
| Service method (read) | `overview()`, `get()` | `ProfileService::overview()` |
| Service method (write) | `create()`, `update()`, `delete()` | `ProfileService::update()` |
| Bootstrap function | `nsa_bootstrap()` | Single entry point |
| Validator | `Validator::rule()` | `Validator::email()`, `Validator::required()` |
| Sanitizer | `Sanitizer::type()` | `Sanitizer::text()`, `Sanitizer::email()` |

### 9.4 Class Naming

All use **PascalCase**:

```php
class ProfileService {}
class ResumeService {}
class Validator {}
class Sanitizer {}
class Response {}
class Session {}
class Jwt {}
class Permissions {}
```

---

## 10. LOGGING & MONITORING (Identical)

### 10.1 Structured Logging

```php
// Log successful action
nsa_log_event(
    type: 'auth.login',
    status: 'success',
    message: 'User logged in successfully',
    details: ['user_id' => 123, 'ip' => $_SERVER['REMOTE_ADDR']]
);

// Log error
nsa_log_event(
    type: 'profile.update',
    status: 'error',
    message: 'Database error during profile update',
    details: ['user_id' => 123, 'request_id' => nsa_request_id()]
);

// Log security event
nsa_log_event(
    type: 'security.csrf_failure',
    status: 'warning',
    message: 'CSRF token validation failed',
    details: ['ip' => $_SERVER['REMOTE_ADDR']]
);
```

### 10.2 Request Correlation

```php
// Every response includes request ID for tracing
$requestId = nsa_request_id();  // Auto-generated, unique per request

nsa_json_response([
    'success'    => true,
    'data'       => $result,
    'request_id' => $requestId,  // Client can reference for support
]);
```

---

## 11. CANONICAL API CREATION CHECKLIST

When creating a **new API endpoint**, follow this exact sequence:

### ✅ Step 1: Create File
```
Assets/Website/Api/V1/Feature/action.php
```

### ✅ Step 2: Bootstrap & Configure
```php
<?php
declare(strict_types=1);

require_once dirname(__DIR__, 4) . '/Connector/_bootstrap.php';

nsa_bootstrap([
    'security'      => true,
    'session'       => true,
    'methods'       => ['GET'],
    'json'          => true,
    'csrf'          => false,  // false for GET, true for POST/PUT/DELETE
]);
```

### ✅ Step 3: Authenticate
```php
$userId = $_SESSION['user_id'] ?? null;
if (!$userId) {
    nsa_json_response(['success' => false, 'message' => 'Unauthorized'], 401);
}
```

### ✅ Step 4: Authorize
```php
$permissions = new Permissions();
if (!$permissions->can($userRole, 'feature.view')) {
    nsa_json_response(['success' => false, 'message' => 'Forbidden'], 403);
}
```

### ✅ Step 5: Get Inputs
```php
$pdo = nsa_db();
$input = nsa_json_body();  // For POST/PUT

// Validate inputs
if (!Validator::email($input['email'] ?? null)) {
    nsa_json_response(['success' => false, 'message' => 'Invalid email'], 400);
}
```

### ✅ Step 6: Call Service
```php
$service = new FeatureService($pdo);
try {
    $result = $service->action($userId, $input);
} catch (ValidationException $e) {
    nsa_json_response(['success' => false, 'message' => $e->getMessage()], 400);
} catch (Exception $e) {
    nsa_log_event('feature.action', 'error', $e->getMessage());
    nsa_json_response(['success' => false, 'message' => 'Server error'], 500);
}
```

### ✅ Step 7: Return Response
```php
nsa_log_event('feature.action', 'success', 'Action completed');
nsa_json_response([
    'success' => true,
    'data'    => $result,
], 200);
```

---

## 12. DATABASE SCHEMA CREATION CHECKLIST

When adding **new tables/columns**:

### ✅ Step 1: Create SQL File
```
Assets/Extras/Sqls/feature_schema_v1.sql
```

### ✅ Step 2: Write Safe Schema
```sql
CREATE TABLE IF NOT EXISTS features (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY uk_user_title (user_id, title),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### ✅ Step 3: Use Prepared Statements
```php
$stmt = $pdo->prepare(
    'SELECT id, title FROM features WHERE user_id = :user_id AND status = :status'
);
$stmt->execute([
    ':user_id' => $userId,
    ':status'  => 'active',
]);
```

### ✅ Step 4: Document in Migration
Add comment to SQL file:
```sql
-- Migration: feature_schema_v1
-- Date: 2026-10-09
-- Author: Nishant
-- Purpose: Add features table for feature management
-- Rollback: DROP TABLE features;
```

---

## 13. SECURITY CHECKLIST FOR NEW ENDPOINTS

Every endpoint must verify:

- [ ] **Authentication**: Is user identified? `$_SESSION['user_id']` or JWT?
- [ ] **Authorization**: Does user have permission? `Permissions::can()`?
- [ ] **CSRF**: If POST/PUT/DELETE and session-based: `csrf => true`
- [ ] **Input Validation**: Are all inputs validated? `Validator::`
- [ ] **Input Sanitization**: Are outputs escaped? `htmlspecialchars()`, `Sanitizer::`
- [ ] **SQL Safety**: Using prepared statements? Bound parameters?
- [ ] **Rate Limiting**: Is sensitive action rate-limited? `nsa_rate_limit()`
- [ ] **Error Handling**: Safe messages? Request ID logged? `try/catch`
- [ ] **Logging**: Audit log for important actions? `nsa_log_event()`
- [ ] **HTTPS**: Enforced in production? `OTASecurity::assertHttpsOrThrow()`
- [ ] **Headers**: Security headers applied? `security => true`
- [ ] **Testing**: Tested with wrong auth? Invalid input? Rate limit?

---

## 14. QUICK REFERENCE TABLE

| Need | Location | Function/Class | Example |
|------|----------|---|---|
| Get DB | Connector | `nsa_db()` | `$pdo = nsa_db()` |
| Bootstrap API | _bootstrap.php | `nsa_bootstrap()` | `nsa_bootstrap(['security'=>true])` |
| Check permission | Connector | `Permissions::can()` | `$permissions->can($role, 'action')` |
| Validate email | Connector | `Validator::email()` | `Validator::email($email)` |
| Sanitize text | Connector | `Sanitizer::text()` | `Sanitizer::text($input)` |
| Return JSON | Connector | `nsa_json_response()` | `nsa_json_response($data, 200)` |
| Log event | Connector | `nsa_log_event()` | `nsa_log_event('type', 'status', 'msg')` |
| Rate limit | Connector | `nsa_rate_limit()` | `nsa_rate_limit('key', 5, 300)` |
| Get request ID | Connector | `nsa_request_id()` | `$id = nsa_request_id()` |
| Parse JSON body | Connector | `nsa_json_body()` | `$data = nsa_json_body()` |
| Business logic | Services/ | `FeatureService` | `new FeatureService($pdo)` |
| Page wrapper | Website/Pages/ | `page.php` | includes Contents & Modules |
| Page content | Website/Contents/ | `page-content.php` | actual markup & logic |

---

## 15. WHAT'S DIFFERENT BETWEEN THE TWO PROJECTS

### NexPlacify Additional Complexity:
- ✅ **Accounts/** - Full user management (profile, resume, onboarding)
- ✅ **Admins/** - Full admin dashboard and management
- ✅ **Services/AI/** - GroqService, PdfResumeReader for AI intelligence
- ✅ **Services/Accounts/** - Readiness, Resume, Profile, Onboarding services
- ✅ **API/V1/** - Explicit versioning of all endpoints
- ✅ **Google OAuth** - More sophisticated authentication
- ✅ **Readiness scoring** - Complex calculation engine

### NileAndSinai Simpler Model:
- ✅ **Website/Api/** - Direct API structure (not versioned)
- ✅ **Products/** - Simple product catalog
- ✅ **Website/Pages/** - Directly organized pages
- ✅ **Fewer services** - Product-focused, not account-focused

### **Core Connector: IDENTICAL**

---

## 16. PLAYBOOK ALIGNMENT

Both projects follow **Central Project Engineering Playbook** principles:

✅ **Section 1 - Core Principles**
- Source of truth: Check existing source before creating
- Small reviewable units: Each API endpoint is discrete
- Preserve architecture: Connector/API/Service/Page separation
- Honest validation: Run syntax checks
- Protect secrets: .env excluded from Git

✅ **Section 2 - Modular Folder Map**
- Both follow recommended structure exactly
- Connector, Website, Modules, Services, Extras organized identically
- Folder boundaries respected in both

✅ **Section 3 - Page Wrapper Pattern**
- Thin wrappers in Pages/
- Content in Contents/
- Shell reuse through Modules/

✅ **Section 4 - API Endpoint Pattern**
- Bootstrap entry point
- Method & permission checks
- Prepared SQL
- Consistent response format
- Audit logging

✅ **Section 5 - Connector Architecture**
- Both implement all Connector components
- Same helper functions
- Same bootstrap options

✅ **Section 6 - Adaptation Checklist**
- Both started from same reference implementation
- Renamed identities (nsa_* prefix)
- Proper .env handling
- Database migrations structured

---

## SUMMARY

**Both projects share:**
1. Identical Connector layer (infrastructure)
2. Identical API creation pattern
3. Identical service layer organization
4. Identical page wrapper pattern
5. Identical security implementations
6. Identical database patterns
7. Identical naming conventions
8. Identical error handling
9. Identical logging approach

**Differences are in:**
- Domain complexity (NexPlacify more complex, Nile simpler)
- Feature scope (NexPlacify has admin/accounts, Nile is product-focused)
- Service count (NexPlacify more services)

**Both strictly follow the Central Project Engineering Playbook**

This means any NEW project can use this exact pattern!
