# Central Modular PHP Project Engineering Playbook

**Purpose:** A reusable operating manual for starting, structuring, extending, reviewing, and handing off modular PHP applications. This is intentionally project-neutral. It describes reusable engineering conventions and the capabilities observed in the reference Connector implementation, while clearly marking what must be adapted for a new application.

**Audience:** Developers, AI coding agents, maintainers, and anyone inheriting the repository.

---

## 1. Core working principles

### 1.1 Establish the source of truth before editing

Before creating or replacing code, inspect in this order:

1. The latest source tree or archive supplied for the active project.
2. Existing route definitions, page wrappers, shared shell, modules, API endpoints, services, and configuration.
3. Current schema migrations/SQL files and, when available, the actual database schema.
4. The project's own technical documentation and handoff notes.
5. External library documentation only when the code actually uses that library or the behavior needs verification.

Do not invent table names, columns, API action names, routes, permissions, include paths, CSS URLs, or status values. If a value is not supported by source, locate it before implementation or state the uncertainty.

### 1.2 Make changes in small, reviewable units

For a new feature, map the UI entry point, route, API contract, service/query logic, authorization, schema dependencies, and tests before editing. Separate unrelated work where possible. Do not rewrite the entire shared shell to change one feature.

### 1.3 Preserve the architecture

- Keep business rules in feature services/API code, not in the Connector infrastructure.
- Keep authentication and authorization on the server. Hiding a button is not authorization.
- Use the existing shared wrappers and navigation. Avoid duplicated headers, footers, shell scripts, or multiple competing notification/loader instances.
- Keep browser URLs and filesystem include paths distinct. A working URL does not establish the matching filesystem path.
- Use canonical runtime filenames in `include`/`require` statements.
- Version suffixes may identify downloadable replacement deliverables, but deployed files and their internal references must use the established canonical names unless the project explicitly uses versioned runtime paths.
- Keep code readable, indented, and commented where the flow is not obvious. Do not minify source code for delivery.

### 1.4 Be honest about validation

Run syntax/static checks that are available and report what was actually checked. PHP syntax success is not an end-to-end test. Do not claim a database round trip, browser interaction, upload, PDF render, push notification, or production deploy succeeded unless it was tested in that environment.

### 1.5 Protect secrets and user data

- Never copy real `.env` values, tokens, database credentials, signing keys, OAuth secrets, or personal data into documentation, source control, or AI prompts.
- Provide `.env.example` with safe placeholders; keep the real `.env` out of version control and out of the public document root where practical.
- Never use production secrets in local tests. Rotate any secret that was committed, logged, exposed, or shipped with an unsafe default.
- Do not expose SQL messages, file paths, stack traces, or exception messages to end users in production. Return a request ID and record diagnostics privately.

---

## 2. Recommended modular folder map

The following is a reference layout, not a mandatory framework. Keep the project's actual names if they already work consistently.

```text
project-root/
├── index.php                     # front controller / route entry, if used
├── .htaccess                     # Apache routing and access rules, if used
├── composer.json
├── composer.lock                 # commit the lock file for reproducible installs
├── .gitignore
├── .env.example                  # safe variable names + placeholders only
├── Assets/
│   ├── Connector/                # reusable infrastructure, not feature rules
│   │   ├── _bootstrap.php        # single loading/initialization entry point
│   │   ├── connector.php         # low-level environment/security/database base
│   │   ├── Auth/                 # session, token, JWT, permission primitives
│   │   ├── Database/             # PDO connection, pool, query builder
│   │   ├── Exceptions/           # normalized exception types
│   │   ├── Helpers/              # response, sanitizer, validator, utilities
│   │   ├── Logger/               # structured event logging
│   │   ├── Security/             # headers, CSRF, origin, request context, limits
│   │   └── Services/             # config, cache, health, API error handling
│   ├── Admins/
│   │   ├── Pages/                # thin authenticated page wrappers
│   │   ├── Contents/             # page-specific HTML/CSS/JS/UI content
│   │   ├── Api/                  # administrative HTTP endpoints
│   │   │   ├── _admin-common.php # shared admin auth/permission/audit glue
│   │   │   └── Feature/index.php
│   │   ├── Services/             # admin/business service classes
│   │   ├── Modules/              # admin shell, CSS, navigation, JS modules
│   │   ├── Database/             # admin-related baseline or migration SQL
│   │   ├── Cron/                 # scheduled jobs, if needed
│   │   └── Uploads/              # protected upload roots, if needed
│   ├── Website/
│   │   └── Pages/                # public/customer-facing page modules
│   ├── Modules/                  # site-wide public shell, assets and utilities
│   └── Extras/
│       ├── Documentations/       # technical docs, guides, handoffs
│       ├── Sqls/                 # SQL migrations/patches/seeds
│       └── Updates/              # changelogs and dated update notes
└── vendor/                       # Composer dependencies; normally not hand-edited
```

### Folder boundaries

| Layer | Owns | Should not own |
|---|---|---|
| `Pages/` | Route-facing page wrapper, access gate if required, page title, head assets, shell composition and content include | Big feature implementations or duplicated shared navigation |
| `Contents/<feature>/` | Feature UI markup, component-specific CSS and browser interactions | Trusted authorization, SQL credentials, direct unvalidated writes |
| `Api/<Feature>/` | HTTP method/action dispatch, request validation, permissions, service invocation, response shape | Unreviewed schema assumptions or business logic duplicated across endpoints |
| `Services/<Feature>/` | Business rules, queries/transactions and reuseable domain operations | HTML rendering or browser navigation |
| `Connector/` | Shared request infrastructure, database access, response normalization, auth primitives, validation, security, logging and cache | Feature-specific statuses, product logic or customer workflow rules |
| `Modules/` | Shared reusable components loaded through the shell | Page-specific side effects without a documented API |
| `Database/` and `Extras/Sqls/` | Versioned schema changes and data seeds | Undocumented production-only manual alterations |

### Where new files go

- A new admin page: create the thin wrapper in `Assets/Admins/Pages/`.
- Its visible feature: `Assets/Admins/Contents/<feature>/<feature>-content.php`.
- Its endpoints: `Assets/Admins/Api/<Feature>/index.php` with an explicit, documented action contract.
- Reusable feature logic: `Assets/Admins/Services/<Feature>/` or the equivalent feature service folder already used by the project.
- Cross-feature server infrastructure: only add to `Assets/Connector/` if the behavior is truly generic.
- Reusable browser behavior for all pages: a shared JS/CSS module included exactly once by the shared shell.
- Schema changes: add a new migration/patch with a date or ordered version, rollback/recovery notes if applicable, and update the schema reference. Do not silently edit an old migration already used by deployments.
- Tests: use the repository's established test layout; if none exists, create a clear `tests/` layout instead of scattering test scripts among production files.

---

## 3. Page wrapper and content-module pattern

A wrapper should be thin and use the real shell already in the project. The structure may look like:

```php
<?php
declare(strict_types=1);

// Establish page-specific shell state here, using existing project conventions.
$pageTitle = 'Feature name';
$activeGroupId = 'feature';
$activeItemId = 'feature';
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?= htmlspecialchars($pageTitle, ENT_QUOTES, 'UTF-8') ?></title>
    <!-- Include the existing shared CSS/scripts using the project's real URLs. -->
</head>
<body>
    <?php include __DIR__ . '/../Modules/topNav.php'; ?>
    <main class="content">
        <?php include __DIR__ . '/../Contents/feature/feature-content.php'; ?>
    </main>
    <?php include __DIR__ . '/../Modules/bottomNav.php'; ?>
</body>
</html>
```

This is an illustrative pattern only. Verify actual relative depths, canonical filenames, shell variables, CSS URLs and permission gates before using it. Never paste this sample over an existing wrapper without reconciling it with the project's conventions.

### Shared shell rules

- A shared navigation module should be loaded once per page.
- Global scripts should be singleton-safe, so duplicate inclusions do not create duplicate event handlers, polls, modals or notifications.
- Keep the page's body content inside the existing shell rather than creating a second shell.
- Central CSS URLs may differ from filesystem paths. Use the URL already present in the working wrappers.
- When adding meta tags, favicons, social images or a global loader, decide whether the target is the public site shell, the admin shell, or both. Do not unintentionally change all three.

---

## 4. API endpoint pattern

A feature endpoint normally needs to:

1. Load the Connector bootstrap or the project's established API bootstrap wrapper.
2. Declare allowed HTTP methods and the request content type/body limit.
3. Authenticate the requester and enforce the exact permission server-side.
4. Parse and validate input; reject unknown actions and malformed payloads.
5. Call a feature service or use a clearly delimited service function.
6. Use prepared SQL statements for values and allowlisted identifiers for table/column/order fragments.
7. Use transactions where multiple writes must succeed or fail together.
8. Write an audit/log event for important mutations, without logging secrets.
9. Return a consistent response and request/correlation ID.
10. Avoid leaking internal errors in production.

An API must not trust a browser-supplied `admin_id`, permission flag, owner ID, final total, tax amount, status, or computed price without server-side authorization and validation. Recalculate financial values on the server.

### Example using the reference Connector bootstrap

For a nested endpoint located at `Assets/Admins/Api/Feature/index.php`, the relative path depth must be confirmed; in the currently observed layout, the connector root is under `Assets/Connector/`:

```php
<?php
declare(strict_types=1);

require_once dirname(__DIR__, 3) . '/Connector/_bootstrap.php';

nsa_bootstrap([
    'security' => true,
    'csp' => true,
    'session' => true,
    'csrf' => true,
    'json' => true,
    'methods' => ['GET', 'POST'],
    'payload_limit' => 1024 * 1024,
    'rate_limit' => null, // Add a meaningful limit for sensitive endpoints.
]);

$pdo = nsa_db();
```

The helper prefix and bootstrap name above come from the reference implementation, not a universal standard. Where the application already has an admin API common layer, follow it instead of bootstrapping the Connector a second time. Do not enable JSON-only validation on multipart file-upload endpoints.

### Consistent response format

The reference `Response` helper emits a shape similar to:

```json
{
  "success": true,
  "message": "Operation completed.",
  "data": {},
  "version": "<configured connector version>"
}
```

Errors use `success: false`, a message, a data object, and a version. In production the error text must be safe; include a request ID in `data` so operators can find the private log entry.

---

## 5. Connector architecture and what its components do

The Connector is infrastructure below APIs and feature services. It centralizes cross-cutting behavior so endpoint code does not reimplement configuration loading, security headers, method checks, payload checks, CSRF, rate limiting, database setup and exception formatting.

### 5.1 `_bootstrap.php`

The reference bootstrap:

- Loads the low-level connector first.
- Loads the Connector `.env` and makes settings available before dependent modules initialize.
- Requires modules in a deterministic order.
- Offers one `nsa_bootstrap(array $options = [])` entry point.
- Initializes request context and centralized exception handling.
- Optionally initializes security/CSP, session, allowed-method checks, JSON content-type validation, payload-size limits, CSRF and rate limiting.
- Exposes database/config/request/logging helper functions.

Options supported in the inspected implementation:

| Option | Purpose | Correct use |
|---|---|---|
| `security` | Run the configured security initialization | Keep enabled for normal production endpoints unless a documented endpoint type requires a different treatment. |
| `csp` | Apply Content Security Policy behavior | Preserve a restrictive policy; do not broadly allow inline scripts or arbitrary origins just to fix a page. |
| `session` | Start the configured PHP session | Enable when endpoint authentication/CSRF needs session state. |
| `csrf` | Require a valid token on state-changing methods | Pair with `session => true`; expose tokens using the established mechanism. |
| `json` | Require JSON request content type | Do not use for `multipart/form-data` uploads unless the contract is explicitly different. |
| `methods` | Allowlist HTTP methods | Use only methods the endpoint needs. |
| `payload_limit` | Limit request body size in bytes | Give upload endpoints a deliberate limit consistent with PHP/server limits. |
| `rate_limit` | Limit requests by a chosen key and window | Choose a key specific to the protected action, such as endpoint + authenticated account or IP. |
| `exception_handler` | Register standardized exception handling | Usually enable for APIs; check boot order if an outer handler already owns errors. |
| `csp_nonce` | Pass a nonce for CSP where supported | Generate securely and use consistently with the returned CSP policy. |

`nsa_bootstrap_status()` provides a diagnostic snapshot of loaded/booted state and options. `nsa_bootstrap_reset()` is primarily useful for controlled tests/long-running processes; ordinary web endpoints should not reset the bootstrap casually.

### 5.2 Helper functions exposed by the reference bootstrap

| Function | Contract / purpose |
|---|---|
| `nsa_bootstrap(array $options = []): array` | Initializes the Connector according to the options above. |
| `nsa_db(): PDO` | Returns the shared PDO connection. Use prepared statements for values. |
| `nsa_config(string $key, mixed $default = null): mixed` | Reads configuration through the config service. |
| `nsa_rate_limit(string $key, int $limit = 60, int $windowSeconds = 60): array` | Applies a rate-limit hit and returns allow/limit metadata; check the `allowed` result. |
| `nsa_request_id(): string` | Gets the current request ID for response/log correlation. |
| `nsa_json_body(): array` | Decodes the JSON request body; empty bodies return an empty array; malformed/non-object-or-array JSON raises a validation exception. |
| `nsa_bootstrap_status(): array` | Returns bootstrap/connector state useful for diagnostics. Restrict detailed diagnostics to authorized operators. |
| `nsa_bootstrap_reset(): void` | Resets bootstrap boot-state in controlled test contexts. |
| `nsa_log_event(...)` | Writes a structured event through the Connector logger. Supply useful type/status/message/details while excluding sensitive values. |

The same codebase also contains lower-level `ota_*` helpers such as `ota_db()`, `ota_json_response()`, `ota_log_event()`, `ota_log_blocker()`, and log-level conveniences (`log_info`, `log_warning`, `log_error`, `log_security`, `log_assessment`). These are compatibility/helper names from the reference Connector. A new project should choose one consistent application prefix or namespace and update all call sites together.

### 5.3 Low-level connector and environment loader

`OTAEnv` in the reference implementation provides:

- `load($path)`: parse an environment file once and expose its variables through `$_ENV`, `$_SERVER`, and the process environment.
- `get($key, $default)`: read loaded/environment values with a fallback.
- `all()`: return the parsed values.
- `loadedPath()` and `loadedFromFile()`: diagnostics about the loaded environment source.

The same file includes low-level security and database facilities:

- Security headers such as content-type sniffing protection, frame protections and referrer policy.
- HTTPS and origin checks with an allowlist from configuration.
- Method checking and client-IP handling.
- PDO connection from driver/host/port/database/user/password/charset settings.
- Connection ping/latency diagnostics.
- Standard JSON response and small utility helpers.

**New-project change required:** rename project-branded classes/constant names and update all references only as one coordinated refactor. Do not rename `OTAEnv` or `NileAndSinaiBootstrap` in one file while leaving dependent files/calls unchanged.

### 5.4 Authentication and permissions primitives

The available primitives include:

- `Session::start()`, `regenerate()`, `set()`, `get()`, `remove()`, `destroy()`.
- `Jwt::encode()` and `Jwt::decode()` using HMAC signing; decoding checks the signature plus `nbf`, `iat`, and `exp` if present.
- `Token::generate()`, `Token::hash()`, `Token::verify()` for opaque token generation/hash verification.
- `Permissions::all()`, `roles()`, `permissionsFor($role)`, `can($role, $permission)`, `canAny(...)`, `canAll(...)`, and `catalog()`.

The current permission map is application-specific, not a universal RBAC policy. Replace it with the new project's roles and permissions. Prefer explicit permissions per action, deny by default, and enforce permissions in every API that reads/writes protected resources.

### 5.5 Database and query building

Available facilities include connection pools and a database facade that expose `get`, `put`, `reset`, `ping`, `pdo`, `prepare`, and `query` methods. The primary helper `nsa_db()` returns PDO.

The `QueryBuilder` supports:

- `QueryBuilder::table($table)`
- `select($columns)`
- `insert($data)`
- `update($data)`
- `delete()`
- `where($column, $value, $operator)`
- `whereNull($column)` and `whereNotNull($column)`
- `orderBy($column, $direction)`
- `limit($limit, $offset)`
- `toSql()` and `bindings()`

The query builder validates identifiers and constructs bound placeholders for values. It is not a reason to pass user-controlled identifiers, sort columns or raw SQL into a query. Use a strict allowlist for dynamic table/column/order fragments.

Typical PDO usage:

```php
$stmt = $pdo->prepare(
    'SELECT id, display_name FROM example_records WHERE id = :id LIMIT 1'
);
$stmt->execute([':id' => $recordId]);
$row = $stmt->fetch(PDO::FETCH_ASSOC) ?: null;
```

Do not interpolate user input into SQL. Avoid repeating named PDO placeholders within one statement because native prepared-statement drivers may reject duplicate parameter names. For MySQL collation conflicts, find the compared columns and explicitly reconcile the correct collation or perform a schema-level consistent collation migration after checking the data/schema; do not blindly convert the whole database.

### 5.6 Helpers, validation and sanitization

- `Response::json($data, $status)`, `Response::success($message, $data, $status)`, `Response::error($message, $status, $data)` end the request with a normalized JSON body.
- `Validator::required`, `email`, `integer`, `boolean`, `uuid`, and `in` provide simple validation predicates. They are small helpers, not a complete schema validation framework.
- `Sanitizer::text`, `array`, `email`, and `filename` provide basic normalization. Sanitization does not replace validation, parameterized SQL, or context-aware output escaping.
- `Utilities` exposes environment access, database access, version, ISO timestamp, masking, and client-IP helpers. Prefer the canonical helper already used by the endpoint rather than mixing interfaces.

Always validate nullability before applying string-only functions such as `mb_substr()`, `trim()` casts where ambiguous, or regular expressions. Make DB column nullability and the API payload contract agree.

### 5.7 Security modules

| Component | Main responsibility |
|---|---|
| `Headers` | Applies response security headers and CSP. |
| `OriginValidator` | Parses and checks allowed origins; can enforce production configuration. |
| `Security` | Coordinates security initialization and request/IP validation. |
| `RequestValidator` | JSON content-type, allowed HTTP method, payload-size checks, request ID and IP helpers. |
| `Csrf` | Session-bound token creation, validation, assertion and rotation. |
| `RequestContext` | Creates/accepts a validated request ID, emits `X-Request-ID`, tracks elapsed time. |
| `RateLimiter` | Enforces configured request limits using its storage mechanism. |
| `DeviceFingerprint` | Generates a fingerprint/risk signal; do not treat it as a standalone identity or authorization factor. |

For state changes from a browser session, require CSRF protection. For machine-to-machine endpoints, use an explicitly designed authentication contract rather than disabling security globally.

### 5.8 Exceptions, cache, health and logs

- Exception types distinguish authentication, authorization, validation, security and rate-limit errors.
- `ApiExceptionHandler::register()` installs the global handler; `handle(Throwable)` maps errors to HTTP status, adds request ID, logs privately, and redacts internal messages in production.
- `CacheService::set`, `get`, `delete`, and `remember` provide TTL-based file cache operations. Ensure cache files are in a non-public directory and its directory is writable by the PHP process.
- `ConfigService::get`, `version`, and `appName` resolve common application config.
- `HealthService::ping` / `status` can inspect DB/service health. Keep detailed health diagnostics private or access-controlled.
- `OTALogger::log`, `logBlocker`, `info`, `warning`, `error`, `security`, and `assessment` plus wrapper functions record structured events. Log request ID, action, result and safe identifiers; redact passwords, tokens, full request bodies and secrets.

---

## 6. How to adapt the Connector for a new project

Do not copy the directory and immediately expose it on a live host. Use this migration checklist.

### Phase A — Inventory and isolate

1. Copy only the Connector source files and required Composer dependencies, not old project tables, customer data, uploads, logs, or production `.env`.
2. Preserve `composer.json` and `composer.lock` as a pair. Run `composer install` in the new app rather than copying a random `vendor/` directory from a different PHP/runtime environment.
3. Record each direct dependency, PHP extension requirement, and package version.
4. Identify every hardcoded root path, URL, host, application name, version, log directory, cache directory, cookie/session name, and CSP source.

### Phase B — Rename identities consistently

The observed Connector contains legacy, mixed identifiers including `OTA*`, `OTAEnv`, `OTADatabase`, `NileAndSinaiBootstrap`, `nsa_*`, and `ota_*`. These identifiers are technically coupled through calls/constants and are not project-neutral by default.

Choose one new app prefix (for example `app_`) or a PHP namespace. Then:

1. Rename constants, classes, session keys, config names and global helper functions in one planned refactor.
2. Update all files in the dependency graph and all calling APIs together.
3. Avoid class-name collisions from unnamespaced classes such as `Response`, `Session`, `Token`, `Validator`, and `Sanitizer` if the new project already uses these names. Namespaces or a consistent prefix are safer than piecemeal renames.
4. If migration needs to be gradual, keep a temporary compatibility layer that calls the new implementation and document a removal date. Do not keep two competing implementations of the same responsibility.
5. Run `grep`/search for every old prefix, class name, constant and config key after refactoring; investigate all remaining references.

### Phase C — Configuration and secrets

1. Create a new `.env.example` containing only variable names and safe placeholders.
2. Create a new actual `.env` outside the public web root where possible; if the server requires it inside the project, deny direct web access at the server layer and test direct URLs for a 403/404.
3. Ensure `.gitignore` contains `.env`, `.env.*`, and explicit exceptions only for safe example files.
4. Generate new random high-entropy `JWT_SECRET`, `TOKEN_SECRET`, API/logging keys and any other signing credentials. Never reuse the previous project's secret values.
5. Remove unsafe hardcoded fallback secrets from token/JWT code. In production, missing required secrets must fail closed with a private diagnostic, not silently sign tokens with a built-in default.
6. Update `APP_ENV`, `APP_NAME`, `APP_VERSION`, `ALLOWED_ORIGINS`, session cookie name, database connection values, CSP origins, logging/cache paths and any provider API configuration.
7. Restrict `.env` and private storage permissions to the PHP runtime/administrator that needs them.

### Phase D — Database and data-model alignment

1. Create a new database and a schema migration plan. Never point the new project to the original production database by default.
2. Review every `CREATE TABLE`, logger query, session/auth query, rate-limit storage operation and cache path. The Connector logger/rate limiter may depend on support tables or files; include those explicitly in the schema/setup documentation.
3. Confirm correct charset/collation, foreign keys, transaction support and indexes for the new driver.
4. Test `nsa_db()` or its renamed equivalent and run the health ping in a private setup command.
5. Execute reads/writes only after the target schema is verified. Do not assume an older SQL export represents the live schema.

### Phase E — Authentication, permissions and security

1. Replace the old permission map with the new role set.
2. Define how users authenticate and which session/token cookie/header is authoritative.
3. Rotate/regenerate sessions after login; invalidate them at logout.
4. Require server-side authorization in each protected endpoint and on individual record ownership boundaries.
5. Configure exact allowed origins; verify HTTPS reverse-proxy behavior only for the proxy configuration you actually trust.
6. Review CSP for the new host/CDN/script sources. Avoid `unsafe-inline` or wildcard hosts unless there is a documented and narrowly scoped reason.
7. Use CSRF for cookie/session-authenticated mutations, rate limit login/password recovery and other sensitive endpoints, and cap request sizes.
8. Ensure public endpoints expose no admin diagnostics or environment/status dumps.

### Phase F — Paths, logs and cache

1. Move rate-limit/cache/log storage to dedicated non-public paths with explicit permissions.
2. Update cron jobs and CLI utilities to load the same environment safely.
3. Ensure rotation/retention works and log writes fail safely without leaking sensitive data.
4. Configure the server to deny direct requests to `.env`, logs, private temp files and backup archives.

### Phase G — Verification before production

Use a staged checklist:

- [ ] PHP version and required extensions are correct.
- [ ] Composer install succeeds from the lock file.
- [ ] No source or docs contain previous project names, secrets, URLs, DB names or permission keys.
- [ ] `.env` is not tracked by Git or directly downloadable.
- [ ] Missing required secrets cause a safe startup failure.
- [ ] DB health ping succeeds using the new database.
- [ ] JSON parse errors return a predictable 4xx response and request ID.
- [ ] Wrong methods return 405 (or the defined method error).
- [ ] Unauthenticated requests return 401; unauthorized users return 403.
- [ ] State-changing requests without/with invalid CSRF tokens fail.
- [ ] Rate limits trigger the defined 429 response.
- [ ] Exceptions are logged privately; production responses do not expose stack traces or SQL.
- [ ] All API reads/writes use known schema and bound parameters.
- [ ] Cache/rate-limit/log directories are non-public and writable only as required.
- [ ] The direct `.env` URL returns 403/404 in the deployed environment.
- [ ] Backup/rollback steps exist before schema/code release.

---

## 7. File delivery, naming and replacement protocol

Use a predictable handoff format for code changes:

```text
release-name/
├── README-DEPLOYMENT.md
└── <original-directory-structure>/
    └── feature-file-vN.php
```

The source delivered as `feature-file-vN.php` is a temporary, versioned artifact used for review/download. When installing it, copy its contents into the established runtime file such as `feature-file.php` unless the project's routing explicitly expects the versioned path.

A deployment guide should list:

- Exact source artifact name.
- Exact canonical destination path.
- Whether to replace the whole file or merge a defined block.
- Dependencies and prerequisite migrations.
- Config keys/permissions required.
- Backup and rollback instructions.
- Tests performed and tests not performed.

Do not rename canonical paths simply because a delivered file includes a version suffix. Do not silently change include paths, route paths, hostnames or central CSS URLs as part of unrelated code changes.

---

## 8. Working with SQL and migrations

- Keep each schema change in a named SQL migration/patch and record the order in which it must be applied.
- Prefer additive, backward-compatible migrations first (create/add), deploy code that handles old/new states if needed, then remove legacy structures only after verification.
- Do not modify an already-deployed migration file to change production history; add a follow-up migration.
- Never invent columns from UI labels. Verify the actual SQL or schema inspection output first.
- Use transactions for logically atomic business operations, with rollback on any exception.
- Never perform automatic `ALTER TABLE` or schema repair from ordinary page requests.
- For legacy collation mismatch, inspect the two compared columns, their collations and the intended database standard before selecting a cast/collation fix. Prefer a planned consistent schema repair when broad enough, and keep query-level handling narrow.
- Audit important mutations with actor, action, entity ID, outcome, request ID and safe metadata.

---

## 9. Browser UI and global modules

- Render reusable UI from a single shared module rather than copying it to many pages.
- Use prefixed CSS classes and DOM IDs for global widgets so they do not collide with feature styles.
- Make initialization idempotent: check for an existing singleton before inserting CSS/DOM, timers or listeners.
- Do not blindly intercept every `fetch()` to display a global loader; background polls and multiple concurrent requests can make the loader flicker or remain stuck. Offer explicit `show/hide/during` APIs and opt-in element attributes.
- For global notifications, request browser permission only after a user gesture, handle denied/unsupported states, and keep an in-page alert when browser notifications are unavailable.
- Use `aria-live`, focus states, keyboard close/open behavior, reduced-motion preferences, responsive layouts, and deliberate z-index levels.
- Keep business confirmation tied to server responses. A progress animation must never claim success before the API confirms it.
- Include shared scripts once through the correct shell, with stable canonical URLs. Check page entry points and wrappers before changing the include target.

---

## 10. Debugging and test workflow

### When an API returns 500

1. Capture the exact response message, HTTP status and request ID.
2. Locate the corresponding private server log by request ID.
3. Reproduce with the smallest request that still fails.
4. Check schema, nullability, parameter naming, transaction state, PHP version and required extensions.
5. Return a safe public error and log the full detail privately in development/controlled logs.
6. Write a regression test where practical.

### When a page appears blank or stuck

1. Check browser Console and Network tabs.
2. Inspect the response code/body for the main HTML and each API call.
3. Confirm selectors and data shapes match the API contract.
4. Check JavaScript parse errors and whether async requests correctly hide loading UI in `finally`.
5. Test a cache-busting hard refresh only after verifying which assets changed.

### Suggested local checks

```powershell
# PHP syntax for an individual file
php -l .\path\to\feature.php

# JavaScript syntax with Node.js installed
node --check .\path\to\feature.js

# Search old prefix/branding references while adapting the Connector
Get-ChildItem .\Assets\Connector -Recurse -File |
    Select-String -Pattern 'NileAndSinai|Nile & Sinai|OTAEnv|OTASecurity|nsa_|ota_'
```

Use the tools available in the developer's actual environment. A local syntax check does not confirm the remote host's PHP version, ownership, filesystem permissions, production schema or network rules.

---

## 11. AI coding-agent handoff template

Give an AI coding agent this context before asking it to modify the codebase:

> Read the source tree and existing docs before editing. Treat the latest source, real schema/migrations, routes, wrappers and Connector implementation as the source of truth. First produce a concise inventory of the target page/API/service and the dependencies it calls. Do not invent routes, table/column names, permissions, CSS URLs or include paths. Keep business logic out of Connector infrastructure and use the existing page wrapper/content/API/service layering. All mutations require authentication, explicit server-side permission checks, validation, prepared SQL, CSRF for session-authenticated browser writes, transaction handling where atomicity is required, and audit logging. Preserve canonical runtime filenames—version suffixes are for downloadable replacement artifacts only. Do not minify code. Make the smallest coherent changes, run syntax/static checks, distinguish verified results from untested behavior, and provide an exact file replacement list, prerequisites and rollback instructions. Never copy `.env` secrets into code, logs, prompts, or documentation.

Before allowing the agent to modify the Connector specifically, also require it to enumerate the Connector's dependency graph, all public helper functions, every current call site, environment keys, server directories, and tests. Require a coordinated rename and regression plan rather than a blind global replacement.

---

## 12. Architecture limits and known adaptation warnings

This playbook intentionally separates general reusable design from reference-specific behavior. The Connector implementation inspected for this playbook has some inherited project identity and mixed helper prefixes. It should be treated as a proven starting point to audit—not as a neutral, secure-by-default package that can be dropped into any new application unchanged.

Important checks before reuse:

1. Remove project-specific class/constant names, permission maps, audit table names, session keys, API origins, asset URLs and feature-specific environment variables.
2. Resolve the mixed `nsa_*` and `ota_*` helper families. Keep one canonical family in the new app or a documented compatibility layer during migration.
3. Replace weak/default JWT/token secret fallbacks. Require high-entropy secrets from configuration in production.
4. Ensure `.env` is ignored by Git and inaccessible over HTTP; the inspected reference `.gitignore` did not itself contain `.env` ignore rules, so add them as part of the new project's setup.
5. Namespacing/prefixing is important because the source uses generic global class names (`Response`, `Session`, `Token`, `Validator`, and others) that may collide when copied into a larger codebase.
6. Review the implementation rather than treating docs as authority when documentation and code disagree. This is especially important for security initialization, token defaults, path resolution and error reporting.
7. Run the full new project's authentication, CSRF, authorization, rate-limit, error-normalization and DB tests before production.

The goal of the Connector is consistent shared behavior with clear security boundaries—not hiding the implementation or making feature APIs depend on magic behavior.

---

## 13. Short implementation checklist for each new feature

- [ ] Confirm route, wrapper, shared shell, permissions and canonical content/API file paths.
- [ ] Confirm the schema and any migration dependency.
- [ ] Put UI into its content module and keep the page wrapper thin.
- [ ] Put endpoint/action logic into the API layer and reusable domain logic into a feature service.
- [ ] Bootstrap the Connector once through the project's canonical entry point.
- [ ] Add method, payload, authentication, authorization, CSRF and rate-limit settings as appropriate.
- [ ] Use prepared SQL, avoid duplicate named placeholders, and handle nullable values explicitly.
- [ ] Use transactions and audit logs for multi-step writes.
- [ ] Keep errors safe and attach a request ID.
- [ ] Test keyboard/responsive/loading/error states, not only the happy path.
- [ ] Run syntax/static checks and document what still needs a real environment test.
- [ ] Deliver a replacement list with canonical paths and a backup/rollback plan.
