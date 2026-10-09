<?php
declare(strict_types=1);

/**
 * OnTrackAssets Connector
 * Version: 1.0.0
 * Purpose: Secure environment loading, database connection, and health checks.
 */

if (!defined('OTA_CONNECTOR_VERSION')) {
    define('OTA_CONNECTOR_VERSION', '1.0.0');
}
if (!defined('OTA_SYSTEM_VERSION')) {
    define('OTA_SYSTEM_VERSION', OTA_CONNECTOR_VERSION);
}
if (!defined('OTA_CONNECTOR_BUILD')) {
    define('OTA_CONNECTOR_BUILD', 'stable');
}

$OTA_CONNECTOR_VERSION = OTA_CONNECTOR_VERSION;
$OTA_SYSTEM_VERSION = OTA_SYSTEM_VERSION;
$OTA_CONNECTOR_META = [
    'name' => 'OnTrackAssets Connector',
    'version' => OTA_CONNECTOR_VERSION,
    'build' => OTA_CONNECTOR_BUILD,
];

if (PHP_SAPI !== 'cli') {
    $script = basename((string)($_SERVER['SCRIPT_NAME'] ?? ''));
    $self = basename(__FILE__);
    if ($script === $self) {
        http_response_code(403);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode([
            'success' => false,
            'message' => 'Direct access denied.',
            'version' => OTA_CONNECTOR_VERSION,
        ], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        exit;
    }
}

final class OTAEnv
{
    private static array $vars = [];
    private static bool $loaded = false;
    private static ?string $loadedPath = null;
    private static bool $loadedFromFile = false;

    public static function load(string $path): void
    {
        if (self::$loaded) {
            return;
        }

        self::$vars = [];
        self::$loadedPath = $path;
        self::$loadedFromFile = false;

        if (!is_file($path) || !is_readable($path)) {
            self::$loaded = true;
            return;
        }

        $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        if ($lines === false) {
            self::$loaded = true;
            return;
        }

        foreach ($lines as $line) {
            $line = trim($line);
            if ($line === '' || str_starts_with($line, '#') || !str_contains($line, '=')) {
                continue;
            }

            [$name, $value] = array_map('trim', explode('=', $line, 2));
            if ($name === '') {
                continue;
            }

            if (
                (str_starts_with($value, '"') && str_ends_with($value, '"')) ||
                (str_starts_with($value, "'") && str_ends_with($value, "'"))
            ) {
                $value = substr($value, 1, -1);
            }

            self::$vars[$name] = $value;
            $_ENV[$name] = $value;
            $_SERVER[$name] = $value;
            putenv("$name=$value");
        }

        self::$loadedFromFile = true;
        self::$loaded = true;
    }

    public static function get(string $key, ?string $default = null): ?string
    {
        if (array_key_exists($key, self::$vars)) {
            return self::$vars[$key];
        }

        $env = getenv($key);
        if ($env !== false && $env !== '') {
            return $env;
        }

        return $_ENV[$key] ?? $_SERVER[$key] ?? $default;
    }

    public static function all(): array
    {
        return self::$vars;
    }

    public static function loadedPath(): ?string
    {
        return self::$loadedPath;
    }

    public static function loadedFromFile(): bool
    {
        return self::$loadedFromFile;
    }
}

final class OTASecurity
{
    public static function applyHeaders(): void
    {
        if (PHP_SAPI === 'cli' || headers_sent()) {
            return;
        }

        header('X-Content-Type-Options: nosniff');
        header('X-Frame-Options: SAMEORIGIN');
        header('Referrer-Policy: strict-origin-when-cross-origin');
        header('Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()');
        header('Cross-Origin-Opener-Policy: same-origin');
        header('Cross-Origin-Resource-Policy: same-origin');
        header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
        header('Pragma: no-cache');
        header('Expires: 0');

        if (self::isHttps()) {
            header('Strict-Transport-Security: max-age=31536000; includeSubDomains; preload');
        }
    }

    public static function isHttps(): bool
    {
        if (PHP_SAPI === 'cli') {
            return true;
        }

        $https = strtolower((string)($_SERVER['HTTPS'] ?? ''));
        $forwarded = strtolower((string)($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? ''));

        return ($https !== '' && $https !== 'off') || $forwarded === 'https';
    }

    public static function assertHttpsOrThrow(): void
    {
        $env = strtolower((string) OTAEnv::get('APP_ENV', 'production'));
        if (in_array($env, ['local', 'development', 'dev'], true)) {
            return;
        }

        if (!self::isHttps()) {
            throw new RuntimeException('HTTPS is required.');
        }
    }

    public static function assertOriginOrThrow(): void
    {
        if (PHP_SAPI === 'cli') {
            return;
        }

        $allowed = self::allowedOrigins();
        if ($allowed === []) {
            return;
        }

        $origin = trim((string)($_SERVER['HTTP_ORIGIN'] ?? ''));
        if ($origin === '') {
            return;
        }

        foreach ($allowed as $allowedOrigin) {
            if (self::originMatches($origin, $allowedOrigin)) {
                return;
            }
        }

        throw new RuntimeException('Origin not allowed.');
    }

    public static function allowedOrigins(): array
    {
        $raw = (string) OTAEnv::get('ALLOWED_ORIGINS', '');
        $list = array_filter(array_map('trim', explode(',', $raw)));
        return array_values($list);
    }

    public static function originMatches(string $origin, string $allowedOrigin): bool
    {
        return hash_equals(rtrim($allowedOrigin, '/'), rtrim($origin, '/'));
    }

    public static function assertRequestMethod(array $allowed = ['GET', 'POST']): void
    {
        if (PHP_SAPI === 'cli') {
            return;
        }

        $method = strtoupper((string)($_SERVER['REQUEST_METHOD'] ?? 'GET'));
        if (!in_array($method, array_map('strtoupper', $allowed), true)) {
            throw new RuntimeException('Method not allowed.');
        }
    }

    public static function clientIp(): string
    {
        foreach (['HTTP_CF_CONNECTING_IP', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR'] as $key) {
            $value = (string)($_SERVER[$key] ?? '');
            if ($value === '') {
                continue;
            }
            if ($key === 'HTTP_X_FORWARDED_FOR' && str_contains($value, ',')) {
                $value = trim(explode(',', $value)[0]);
            }
            return $value;
        }

        return 'unknown';
    }
}

final class OTADatabase
{
    private static ?PDO $pdo = null;

    private static function ensureEnvLoaded(): void
    {
        OTAEnv::load(__DIR__ . DIRECTORY_SEPARATOR . '.env');
    }

    public static function connection(): PDO
    {
        self::ensureEnvLoaded();

        if (self::$pdo instanceof PDO) {
            return self::$pdo;
        }

        $driver = strtolower((string) OTAEnv::get('DB_DRIVER', 'mysql'));
        $host = (string) OTAEnv::get('DB_HOST', '127.0.0.1');
        $port = (string) OTAEnv::get('DB_PORT', '3306');
        $name = (string) OTAEnv::get('DB_NAME', '');
        $user = (string) OTAEnv::get('DB_USER', '');
        $pass = (string) OTAEnv::get('DB_PASS', '');
        $charset = (string) OTAEnv::get('DB_CHARSET', 'utf8mb4');

        if ($name === '') {
            throw new RuntimeException('Database name is missing.');
        }

        $dsn = match ($driver) {
            'mysql' => "mysql:host={$host};port={$port};dbname={$name};charset={$charset}",
            'pgsql', 'postgres', 'postgresql' => "pgsql:host={$host};port={$port};dbname={$name}",
            'sqlite' => "sqlite:" . $name,
            default => throw new RuntimeException('Unsupported database driver.'),
        };

        $pdo = new PDO($dsn, $user, $pass, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
            PDO::ATTR_PERSISTENT => false,
        ]);

        self::$pdo = $pdo;
        return $pdo;
    }

    public static function reset(): void
    {
        self::$pdo = null;
    }

    public static function pingConnection(?PDO $pdo = null): array
    {
        $pdo ??= self::connection();
        $start = microtime(true);

        $stmt = $pdo->query('SELECT 1 AS alive');
        $row = $stmt ? $stmt->fetch() : false;

        $elapsedMs = (int) round((microtime(true) - $start) * 1000);

        return [
            'alive' => $row && (int)($row['alive'] ?? 0) === 1,
            'latency_ms' => $elapsedMs,
            'driver' => $pdo->getAttribute(PDO::ATTR_DRIVER_NAME),
            'server_version' => $pdo->getAttribute(PDO::ATTR_SERVER_VERSION),
        ];
    }

    public static function prepare(string $sql): PDOStatement
    {
        return self::connection()->prepare($sql);
    }

    public static function query(string $sql): PDOStatement
    {
        return self::connection()->query($sql);
    }
}

function ota_json_response(array $payload, int $status = 200): never
{
    if (PHP_SAPI !== 'cli' && !headers_sent()) {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
    }

    echo json_encode($payload, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    exit;
}

function ota_mask_string(?string $value, int $visible = 3): string
{
    $value = (string) $value;
    $length = strlen($value);
    if ($value === '') {
        return '';
    }
    if ($length <= $visible) {
        return str_repeat('*', $length);
    }
    return substr($value, 0, $visible) . str_repeat('*', max(0, $length - $visible));
}

function ota_ping_connection(?PDO $pdo = null): array
{
    try {
        return [
            'success' => true,
            'version' => OTA_CONNECTOR_VERSION,
            'checked_at' => gmdate('c'),
            'result' => OTADatabase::pingConnection($pdo),
        ];
    } catch (Throwable $e) {
        return [
            'success' => false,
            'version' => OTA_CONNECTOR_VERSION,
            'checked_at' => gmdate('c'),
            'error' => $e->getMessage(),
        ];
    }
}

function ping_connection(?PDO $pdo = null): array
{
    return ota_ping_connection($pdo);
}

function ota_db(): PDO
{
    return OTADatabase::connection();
}

function ota_bootstrap_connector(): PDO
{
    $baseDir = __DIR__;
    OTAEnv::load($baseDir . DIRECTORY_SEPARATOR . '.env');

    OTASecurity::applyHeaders();
    OTASecurity::assertHttpsOrThrow();
    OTASecurity::assertOriginOrThrow();

    return OTADatabase::connection();
}

function ota_connector_bootstrap_once(): PDO
{
    static $bootstrapped = false;
    if ($bootstrapped) {
        return OTADatabase::connection();
    }

    $bootstrapped = true;
    return ota_bootstrap_connector();
}

function ota_connector_env_report(): array
{
    $envPath = __DIR__ . DIRECTORY_SEPARATOR . '.env';

    return [
        'env_path' => $envPath,
        'env_exists' => is_file($envPath),
        'env_readable' => is_readable($envPath),
        'env_loaded_path' => OTAEnv::loadedPath(),
        'env_loaded_from_file' => OTAEnv::loadedFromFile(),
        'db_name_present' => OTAEnv::get('DB_NAME', '') !== '',
        'db_driver' => OTAEnv::get('DB_DRIVER', ''),
        'app_env' => OTAEnv::get('APP_ENV', ''),
    ];
}
