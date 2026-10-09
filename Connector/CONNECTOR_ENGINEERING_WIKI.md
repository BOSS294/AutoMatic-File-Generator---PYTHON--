# Connector Engineering Wiki

> Internal technical specification and AI handoff document for the reusable PHP Connector infrastructure.

**Purpose:** This document is the canonical context an engineer, maintainer, reviewer, or AI coding agent should read before modifying the Connector.

**Owner / Creator:** Mayank Chawdhari aka BOSS294  
**Organization:** Privonix Technologies  
**Target:** PHP 8.1+  
**Bootstrap:** `_bootstrap.php`  
**Connector philosophy:** centralized, reusable, security-oriented infrastructure

---

# 1. Mission

The Connector is a reusable infrastructure layer that sits below application APIs and server-side PHP code.

Its responsibilities include:

```text
Configuration
Database
Authentication
Sessions
Permissions
Security
Request validation
CSRF
Rate limiting
Caching
Logging
Request correlation
Exception normalization
API responses
Health checks
```

It is not the business layer.

The Connector should make application code simpler without hiding important security behavior.

---

# 2. Mental Model for Future AI Agents

Before changing any Connector file, think of the system as:

```text
Application
   │
   ▼
API Endpoint
   │
   ▼
Connector Bootstrap
   │
   ├── Environment
   ├── Request Context
   ├── Security
   ├── Validation
   ├── Authentication
   ├── Authorization
   ├── Database
   ├── Rate Limiting
   ├── Logging
   ├── Cache
   └── Exceptions / Responses
```

The Connector is infrastructure.

Business rules belong above it.

---

# 3. Canonical Entry Point

The preferred entry point is:

```text
Connector/_bootstrap.php
```

An API should normally start with:

```php
require_once dirname(__DIR__, 2) . '/Connector/_bootstrap.php';
```

Then initialize:

```php
nsa_bootstrap();
```

The bootstrap itself loads the Connector dependency graph only once.

---

# 4. Bootstrap Contract

## Function

```php
nsa_bootstrap(array $options = []): array
```

## Default options

```php
[
    'security' => true,
    'csp' => true,
    'session' => false,
    'csrf' => false,
    'json' => false,
    'methods' => null,
    'payload_limit' => null,
    'rate_limit' => null,
    'exception_handler' => true,
]
```

## Meaning

### `security`

Runs:

```php
Headers::apply();
OriginValidator::assertConfiguredForProduction();
OTASecurity::assertHttpsOrThrow();
OTASecurity::assertOriginOrThrow();
Headers::applyCsp();
RequestContext::init();
```

Use:

```php
'security' => true
```

for normal production APIs.

---

### `csp`

Controls CSP generation.

```php
'csp' => true
```

CSP is currently strongest for browser-facing endpoints/pages.

Do not casually loosen `script-src`, `object-src`, `frame-ancestors`, or `default-src`.

---

### `session`

Starts the configured PHP session.

```php
'session' => true
```

Only enable when the API actually requires cookie/session state.

---

### `csrf`

Enables CSRF validation.

It requires:

```php
'session' => true,
'csrf' => true,
```

For state-changing requests, validation is triggered for:

```text
POST
PUT
PATCH
DELETE
```

The default token location is:

```text
X-CSRF-Token
```

with a fallback to:

```text
POST _csrf
```

---

### `json`

Requires:

```text
Content-Type: application/json
```

Use for JSON APIs.

Do not enable it for endpoints intentionally consuming:

```text
multipart/form-data
application/x-www-form-urlencoded
```

unless the endpoint contract changes accordingly.

---

### `methods`

Restricts allowed HTTP methods.

Example:

```php
'methods' => ['POST']
```

Never accept methods an endpoint does not need.

---

### `payload_limit`

Restricts request body size.

Example:

```php
'payload_limit' => 1024 * 1024
```

This is 1 MiB.

Use larger values only where the endpoint genuinely needs them.

---

### `rate_limit`

Example:

```php
'rate_limit' => [
    'key' => 'login:' . Security::clientIp(),
    'limit' => 10,
    'window' => 60,
]
```

The `key` must identify the resource being protected.

Typical key sources:

```text
IP
User ID
Session ID
Endpoint + IP
Endpoint + authenticated user
```

Never blindly use the entire raw request as a key.

---

# 5. Bootstrap Runtime Order

Current intended order:

```text
1. Load dependencies
2. Initialize RequestContext
3. Register ApiExceptionHandler
4. Initialize Security
5. Start Session if requested
6. Validate HTTP method
7. Validate JSON content type
8. Validate payload size
9. Validate CSRF if requested
10. Apply RateLimiter
11. Business logic
```

If an early security/validation step throws, business logic should not run.

---

# 6. Request Context

File:

```text
Security/RequestContext.php
```

Main API:

```php
RequestContext::init(): string
RequestContext::id(): string
RequestContext::elapsedMs(): int
```

Wrapper:

```php
nsa_request_id(): string
```

The request ID is also emitted as:

```text
X-Request-ID
```

The purpose is observability.

Do not use the request ID as:

- an authentication credential
- a session secret
- a CSRF token
- a password-reset token

It is a correlation identifier.

---

# 7. Security Headers

File:

```text
Security/Headers.php
```

API:

```php
Headers::apply();
Headers::applyCsp(?string $nonce = null);
```

The underlying `connector.php` also provides baseline security headers.

The hardened layer adds CSP orchestration.

Do not remove a security header just because a browser request "works" without it.

---

# 8. Origin Validation

File:

```text
Security/OriginValidator.php
```

API:

```php
OriginValidator::allowed(): array
OriginValidator::isAllowed(?string $origin): bool
OriginValidator::assertAllowed(?string $origin = null): void
OriginValidator::assertConfiguredForProduction(): void
```

Production:

```text
ALLOWED_ORIGINS must be configured
```

Development may intentionally be more permissive.

Important distinction:

### No Origin header

May indicate:

- server-to-server request
- CLI request
- API client
- browser behavior where Origin is not sent

### Invalid Origin

Means a browser-origin request claims an origin that is not trusted.

Do not treat "no Origin" and "invalid Origin" as the same thing.

---

# 9. Request Validation

File:

```text
Security/RequestValidator.php
```

Functions:

```php
RequestValidator::ensureJsonRequest();
RequestValidator::ensureMethod([...]);
RequestValidator::payloadSizeLimit($bytes);
RequestValidator::requestId();
RequestValidator::clientIp();
```

Do not use `ensureJsonRequest()` on multipart upload APIs.

---

# 10. CSRF

File:

```text
Security/Csrf.php
```

API:

```php
Csrf::token(): string
Csrf::validate(?string $token): bool
Csrf::assertValid(?string $token = null): void
Csrf::rotate(): string
```

When a user is authenticated with session cookies, CSRF becomes important because browsers automatically attach cookies.

A stateless bearer-token API may not need CSRF in the same way, depending on how credentials are transported.

---

# 11. Rate Limiting

File:

```text
Security/RateLimiter.php
```

API:

```php
RateLimiter::hit(
    string $key,
    int $limit = 60,
    int $windowSeconds = 60
): array
```

Wrapper:

```php
nsa_rate_limit($key, $limit, $windowSeconds)
```

Result shape:

```php
[
    'allowed' => bool,
    'count' => int,
    'limit' => int,
    'windowSeconds' => int,
    'remaining' => int,
    'retry_after' => int,
]
```

Implementation uses filesystem state and an exclusive file lock.

### Important scaling constraint

This is a single-node solution.

If the application runs:

```text
Server A
Server B
Server C
```

each server can otherwise have separate limiter state.

At that point, use a shared backend such as Redis.

---

# 12. Database Layer

Directory:

```text
Database/
```

## Database.php

Core PDO connection.

Important primitives from the existing Connector:

```php
OTADatabase::connection();
OTADatabase::reset();
OTADatabase::pingConnection();
OTADatabase::prepare();
OTADatabase::query();
```

PDO is configured for:

```text
PDO::ERRMODE_EXCEPTION
PDO::FETCH_ASSOC
ATTR_EMULATE_PREPARES = false
ATTR_PERSISTENT = false
```

---

## ConnectionPool.php

Provides named connection references.

```php
OTAConnectionPool::get($key);
OTAConnectionPool::put($key, $pdo);
OTAConnectionPool::reset($key);
OTAConnectionPool::ping($key);
```

Facade:

```php
OTADatabaseFacade::pdo();
OTADatabaseFacade::ping();
OTADatabaseFacade::prepare();
OTADatabaseFacade::query();
```

Legacy/public wrapper:

```php
ConnectionPool::get();
ConnectionPool::ping();
ConnectionPool::reset();
```

---

# 13. QueryBuilder

File:

```text
Database/QueryBuilder.php
```

Core API:

```php
QueryBuilder::table($table)
    ->select([...])
    ->where($column, $value, $operator)
    ->orderBy($column, $direction)
    ->limit($limit, $offset);
```

Mutation:

```php
QueryBuilder::table('users')->insert($data);
QueryBuilder::table('users')->update($data)->where('id', $id);
QueryBuilder::table('users')->delete()->where('id', $id);
```

Compilation:

```php
$sql = $query->toSql();
$bindings = $query->bindings();
```

Important security rule:

### Values

Must use bindings.

### Identifiers

Must pass the identifier validator.

Never add arbitrary user-provided SQL expressions to this builder without explicitly extending the grammar safely.

---

# 14. Authentication

Directory:

```text
Auth/
```

---

## JWT

File:

```text
Auth/Jwt.php
```

API:

```php
Jwt::encode(array $payload, ?string $secret = null): string
Jwt::decode(string $jwt, ?string $secret = null): array
```

Existing JWT format:

```text
HS256
```

Current decoder performs signature verification and time validation.

### AI maintenance warning

Do not casually change the JWT algorithm, secret handling, or validation rules.

Before modifying JWT behavior, review all token-producing and token-consuming endpoints.

A future hardening pass should additionally enforce application-specific:

```text
iss
aud
sub
jti
iat
exp
```

where appropriate.

---

# 15. Token Utility

File:

```text
Auth/Token.php
```

Functions:

```php
Token::generate($bytes);
Token::hash($value);
Token::verify($value, $hash);
```

Typical usage:

```php
$plain = Token::generate();
$stored = Token::hash($plain);
```

Never store a security-sensitive raw token when a server-side hash is sufficient.

---

# 16. Session

File:

```text
Auth/Session.php
```

API:

```php
Session::start();
Session::regenerate();
Session::set($key, $value);
Session::get($key, $default);
Session::remove($key);
Session::destroy();
```

Session cookies use:

```text
HttpOnly
Secure when HTTPS
SameSite=Strict
use_strict_mode
cookies only
```

After successful authentication:

```php
Session::regenerate();
```

should be considered part of login hardening to prevent session fixation.

---

# 17. Permissions

File:

```text
Auth/Permissions.php
```

API:

```php
Permissions::can($role, $permission);
Permissions::permissionsFor($role);
```

Example:

```php
if (!Permissions::can($role, 'manage_users')) {
    throw new AuthorizationException();
}
```

Authentication asks:

> Who is the user?

Authorization asks:

> What is the user allowed to do?

Never confuse the two.

---

# 18. Helpers

Directory:

```text
Helpers/
```

---

## Response

```php
Response::json($data, $status);
Response::success($message, $data, $status);
Response::error($message, $status, $data);
```

Standard success structure:

```json
{
  "success": true,
  "message": "...",
  "data": {},
  "version": "..."
}
```

Standard error structure:

```json
{
  "success": false,
  "message": "...",
  "data": {},
  "version": "..."
}
```

Do not manually construct a second incompatible API response format unless a legacy contract explicitly requires it.

---

## Validator

```php
Validator::required();
Validator::email();
Validator::integer();
Validator::boolean();
Validator::uuid();
Validator::in();
```

---

## Sanitizer

```php
Sanitizer::text();
Sanitizer::array();
Sanitizer::email();
Sanitizer::filename();
```

---

## Utilities

```php
Utilities::env();
Utilities::db();
Utilities::version();
Utilities::nowIso();
Utilities::mask();
Utilities::clientIp();
```

---

# 19. Logging

Directory:

```text
Logger/
```

Files:

```text
LogTypes.php
oLogger.php
```

Types:

```php
LogTypes::INFO
LogTypes::SUCCESS
LogTypes::WARNING
LogTypes::BLOCKED
LogTypes::ERROR
LogTypes::CRITICAL
```

Sources:

```php
LogTypes::SOURCE_PHP
LogTypes::SOURCE_JS
LogTypes::SOURCE_API
LogTypes::SOURCE_SYSTEM
```

---

# 20. Logging API

Preferred convenience functions:

```php
log_info(...)
log_warning(...)
log_error(...)
log_security(...)
log_assessment(...)
```

Generic:

```php
ota_log_event(...)
```

Blocker:

```php
ota_log_blocker(...)
```

Bootstrap wrapper:

```php
nsa_log_event(...)
```

The logger records request context such as:

```text
request method
request path
request origin
request IP
user agent
device fingerprint
request/correlation information
```

The hardened implementation enriches log details with request ID and execution metadata.

---

# 21. Logging Safety Rule

**A logger must not become a single point of failure for the API.**

If database logging fails:

```text
API business operation
        │
        ├── succeeds
        │
        └── logger fails
```

the request should normally still be able to complete.

The logger therefore catches logging failures and reports them through the server error log.

---

# 22. Cache

File:

```text
Services/CacheService.php
```

API:

```php
CacheService::set($key, $value, $ttl);
CacheService::get($key, $default);
CacheService::delete($key);
CacheService::remember($key, $ttl, $callback);
```

Current implementation uses filesystem/temp storage.

Do not use this as a guaranteed distributed cache.

---

# 23. Configuration

File:

```text
Services/ConfigService.php
```

API:

```php
ConfigService::get($key, $default);
ConfigService::version();
ConfigService::appName();
```

Wrapper:

```php
nsa_config($key, $default);
```

Environment loading ultimately comes from `connector.php`.

---

# 24. Health

File:

```text
Services/HealthService.php
```

API:

```php
HealthService::ping($pdo);
HealthService::status();
```

Health status should be used for:

- diagnostics
- deployment validation
- operations
- monitoring

Do not expose sensitive environment values through health output.

---

# 25. Exception Model

Directory:

```text
Exceptions/
```

Classes:

```text
AuthenticationException
AuthorizationException
ValidationException
RateLimitException
SecurityException
```

Use semantic exceptions instead of:

```php
throw new Exception('something failed');
```

when the error category is known.

This allows the centralized API handler to map the error to an appropriate HTTP status.

---

# 26. ApiExceptionHandler

File:

```text
Services/ApiExceptionHandler.php
```

Function:

```php
ApiExceptionHandler::register();
```

Unhandled exceptions are converted to standardized JSON responses.

Known mappings:

```text
AuthenticationException → 401
AuthorizationException  → 403
SecurityException       → 403
ValidationException     → 422
RateLimitException      → 429
```

Other errors:

```text
valid HTTP 4xx/5xx code → preserved where appropriate
otherwise                → 500
```

Production should avoid returning stack traces, file paths, SQL errors, or internal implementation details.

Development can expose more detail when explicitly configured.

---

# 27. Recommended API Templates

## GET API

```php
<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/Connector/_bootstrap.php';

nsa_bootstrap([
    'security' => true,
    'methods' => ['GET'],
]);

$pdo = nsa_db();

$stmt = $pdo->prepare(
    'SELECT id, name FROM items ORDER BY id DESC LIMIT 50'
);

$stmt->execute();

Response::success(
    'Items loaded.',
    [
        'items' => $stmt->fetchAll(),
        'request_id' => nsa_request_id(),
    ]
);
```

---

## JSON POST API

```php
<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/Connector/_bootstrap.php';

nsa_bootstrap([
    'security' => true,
    'json' => true,
    'methods' => ['POST'],
    'payload_limit' => 1024 * 1024,
]);

$data = nsa_json_body();
```

---

## Session API

```php
nsa_bootstrap([
    'security' => true,
    'session' => true,
    'methods' => ['GET', 'POST'],
]);
```

---

## Session mutation API with CSRF

```php
nsa_bootstrap([
    'security' => true,
    'session' => true,
    'csrf' => true,
    'json' => true,
    'methods' => ['POST'],
]);
```

---

# 28. Authentication + Authorization Pattern

Recommended conceptual order:

```text
Request
  ↓
Security
  ↓
Authentication
  ↓
Authorization
  ↓
Input validation
  ↓
Business operation
```

Do not perform expensive business/database operations before deciding whether the caller is authorized to perform them.

---

# 29. What Belongs in Connector

Good Connector responsibilities:

```text
PDO setup
JWT primitives
Session handling
Permission primitives
Headers
CSRF
Origin
Rate limiting
Validation
Sanitization
Logging
Caching
Request IDs
Exceptions
Response formatting
Health checks
Configuration
```

---

# 30. What Does NOT Belong in Connector

Do not put application business rules here:

```text
Product checkout
Jewellery pricing
Order workflows
Customer-specific rules
Website rendering
Marketing content
Product recommendation
Domain-specific calculations
```

Those belong in the application's service/controller/domain layer.

---

# 31. Security Boundaries

The Connector is security infrastructure, but it does not make unsafe business code safe automatically.

Examples:

### Prepared statements

Good:

```php
$stmt = $pdo->prepare(
    'SELECT * FROM users WHERE id = :id'
);
$stmt->execute([':id' => $id]);
```

Bad:

```php
$pdo->query(
    'SELECT * FROM users WHERE id = ' . $_GET['id']
);
```

### QueryBuilder

Use its identifier validation, but do not bypass it by injecting arbitrary SQL fragments.

### Sanitization

Do not treat `Sanitizer::text()` as authorization.

### Authentication

Do not assume:

```text
authenticated = authorized
```

---

# 32. Important Existing Compatibility APIs

The original Connector already exposes legacy/helper APIs.

Do not remove them without auditing application usage.

Examples:

```php
ota_db();
ping_connection();
ota_ping_connection();
ota_json_response();

Utilities::db();
Utilities::version();

ConnectionPool::get();
ConnectionPool::ping();
ConnectionPool::reset();

OTALogger::info();
OTALogger::warning();
OTALogger::error();
OTALogger::security();
OTALogger::assessment();
```

Compatibility should be preserved when hardening internals.

---

# 33. AI Modification Protocol

When another AI is asked to modify this Connector, it should follow this sequence.

## Step 1 — Read the architecture

Read:

```text
_bootstrap.php
connector.php
Auth/*
Database/*
Helpers/*
Logger/*
Security/*
Services/*
Exceptions/*
```

Do not change a file based only on its filename.

---

## Step 2 — Find dependency relationships

Before modifying a class, inspect what imports it.

Example:

```text
Jwt
 └── connector.php
       └── OTAEnv
       └── OTASecurity
```

Do not create a circular dependency.

---

## Step 3 — Preserve compatibility

Before removing a public method:

```text
Search all application APIs.
Search all PHP files.
Search tests.
Search legacy wrappers.
```

Only remove after usage has been audited.

---

## Step 4 — Do not duplicate infrastructure

If a capability already exists, improve and reuse it.

Bad:

```php
function myOwnRateLimiter() {}
```

when:

```php
RateLimiter::hit()
```

already exists.

---

## Step 5 — Prefer centralized fixes

If every API has the same security issue:

```text
Fix Connector
```

rather than:

```text
Fix 40 APIs independently
```

unless the problem is deliberately endpoint-specific.

---

## Step 6 — Test syntax

Every changed PHP file must pass:

```bash
php -l path/to/file.php
```

---

## Step 7 — Integration-test the Connector

At minimum verify:

```text
bootstrap loads
database connects
API response works
security headers appear
Origin enforcement works
request ID exists
JSON parsing works
exceptions serialize correctly
rate limit increments atomically
logging failure does not kill request
session mode works
CSRF mode works
```

---

# 34. Do Not Invent Environment Variables

Before introducing:

```text
NEW_VARIABLE=
```

check whether an equivalent environment variable already exists.

Current known configuration includes categories such as:

```text
APP_NAME
APP_ENV
APP_VERSION
CONNECTOR_VERSION

DB_DRIVER
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASS
DB_CHARSET

ALLOWED_ORIGINS

LOG_LEVEL
LOG_RETENTION_DAYS
LOG_API_KEY

SESSION_NAME

CACHE_PREFIX
CACHE_TTL

GOOGLE_OAUTH_*

JWT_SECRET
TOKEN_SECRET
```

The environment file itself is deployment configuration and must not be published publicly.

---

# 35. Current Hardening Status

The hardened architecture includes:

```text
✓ Central bootstrap
✓ Deterministic dependency loading
✓ PDO infrastructure
✓ Safer QueryBuilder identifiers
✓ Atomic file rate limiting
✓ Security header facade
✓ CSP support
✓ Production origin configuration enforcement
✓ JSON request validation
✓ Payload limits
✓ Request context / request IDs
✓ CSRF support
✓ Central API exceptions
✓ Semantic exception classes
✓ Structured logging
✓ Best-effort logger behavior
✓ Device/risk fingerprint
✓ Session infrastructure
✓ JWT infrastructure
✓ Permissions
✓ Cache service
✓ Health service
✓ Configuration service
✓ Standardized responses
```

---

# 36. Remaining High-Priority Hardening

The following items must be considered separately because they affect deployment/security policy.

## Secret management

Do not ship hardcoded credential fallbacks.

The JWT and token secret strategy must use strong deployment secrets.

---

## Secret rotation

If a real production secret has been exposed in any public or shared context:

```text
rotate it
invalidate old credentials
deploy new secret
```

---

## Multi-server scaling

Filesystem cache and rate limiting are local-node mechanisms.

For horizontally scaled deployment, migrate shared state to a centralized backend.

---

## JWT claim policy

A future hardening pass should explicitly define:

```text
issuer
audience
subject
JWT ID
issued-at
not-before
expiry
```

rather than relying only on signature validity and timestamps.

---

# 37. Connector Rules for Future Features

When adding a new feature, decide which layer owns it.

| Requirement | Layer |
|---|---|
| SQL connection | Database |
| SQL query composition | Database |
| JWT | Auth |
| User session | Auth |
| Permission | Auth |
| HTTP headers | Security |
| CSRF | Security |
| Origin | Security |
| Rate limiting | Security |
| Input validation | Helpers/Security |
| Logging | Logger |
| Cache | Services |
| Health check | Services |
| Runtime error normalization | Exceptions/Services |
| Business workflow | Application layer |

---

# 38. Naming Conventions

Current naming patterns include:

```text
OTA*                  Connector core classes
nsa_*                 New public bootstrap helper functions
Session               Session facade
Security              Security facade
RequestContext        Request correlation
ApiExceptionHandler   API-level error normalization
```

When adding new global helper functions, prefer:

```text
nsa_*
```

to avoid generic global-function collisions.

---

# 39. Public API Stability

Classes and functions already consumed by application code should be considered public infrastructure APIs.

When changing behavior:

1. document the change
2. check application usage
3. preserve backward compatibility where reasonable
4. run syntax checks
5. run integration tests
6. document migration instructions if behavior changes

---

# 40. Design Goal

The ideal API should be able to say:

```php
require_once dirname(__DIR__, 2) . '/Connector/_bootstrap.php';

nsa_bootstrap([
    'security' => true,
    'json' => true,
    'methods' => ['POST'],
]);

// Business logic starts here.
```

That is the point of the architecture.

The Connector handles the infrastructure.

The API handles the business operation.

---

# 41. Final AI Handoff Contract

Any future AI working on this codebase should assume:

```text
1. Connector is shared infrastructure.
2. Breaking compatibility is expensive.
3. Security behavior must be centralized.
4. Secrets must never be hardcoded into source.
5. SQL values must be bound.
6. SQL identifiers must be validated.
7. Session APIs need CSRF protection for state-changing browser requests.
8. Rate limiting is currently single-node unless replaced by shared storage.
9. Logging must not become a fatal dependency.
10. Errors should become standardized API responses.
11. Request IDs should be preserved through logs and responses.
12. Business logic does not belong in Connector.
13. Every changed PHP file must pass php -l.
14. Integration behavior must be tested before declaring a change production-ready.
15. Existing public APIs must be audited before removal or rename.
```

---

# 42. Suggested Future Connector Roadmap

```text
Phase 1
✓ Bootstrap
✓ Security
✓ Validation
✓ Logging
✓ Exceptions
✓ Request context
✓ Rate limiting

Phase 2
→ Strong authentication policy
→ JWT issuer/audience/JTI enforcement
→ Secret provider abstraction
→ Redis adapter
→ Database transaction helper
→ Retry-safe service primitives

Phase 3
→ Automated Connector tests
→ Security test suite
→ Integration test harness
→ Static analysis
→ CI pipeline
→ API contract tests

Phase 4
→ Distributed cache
→ Distributed rate limiter
→ Metrics
→ OpenTelemetry-compatible tracing
→ Structured JSON logs
```

---

# 43. One-Sentence Definition

**The Connector is the security, persistence, observability, validation, and runtime infrastructure layer that allows PHP APIs to remain small, consistent, secure, and focused on application business logic.**

---

## Ownership

Created by:

**Mayank Chawdhari aka BOSS294**

**Privonix Technologies**

Copyright © 2026.

This document is intended to preserve architectural context for developers and AI coding agents working on the Connector.
