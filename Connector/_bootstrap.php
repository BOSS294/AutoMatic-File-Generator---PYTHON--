<?php
declare(strict_types=1);

/**
 * ============================================================================
 * NileAndSinai V2 - Connector Bootstrap
 * ============================================================================
 *
 * Version      : 2.0.0
 * Connector    : 1.0.1+
 * Project      : NileAndSinai V2
 *
 * Created by   : Mayank Chawdhari aka BOSS294
 * Organization : Privonix Technologies
 *
 * Copyright / Trademark
 * ---------------------
 * © 2026 Mayank Chawdhari / Privonix Technologies.
 * NileAndSinai and associated branding are project marks where applicable.
 * All rights reserved.
 *
 * PURPOSE
 * -------
 * Single entry point for Connector infrastructure. It loads the full stack
 * and optionally initializes security, sessions, request correlation,
 * rate-limiting, JSON validation and centralized API exception handling.
 *
 * Typical API:
 *
 *   require_once dirname(__DIR__, 2) . '/Connector/_bootstrap.php';
 *   nsa_bootstrap([
 *       'security' => true,
 *       'session'  => false,
 *       'methods'  => ['GET', 'POST'],
 *   ]);
 *
 *   $pdo = nsa_db();
 *
 * FEATURES
 * --------
 * - Deterministic Connector dependency loading.
 * - Request ID / correlation header.
 * - Security headers + CSP.
 * - HTTPS/origin enforcement.
 * - Optional session and CSRF support.
 * - Optional JSON/method/payload validation.
 * - Atomic single-server rate limiting.
 * - Centralized API exception handling.
 * - Shared PDO/database helpers.
 * - Shared logging/configuration helpers.
 *
 * NOTE
 * ----
 * This file intentionally does not change the existing JWT secret fallback
 * behavior. Secret rotation/hardening is a separate change.
 * ============================================================================
 */

const NSA_BOOTSTRAP_VERSION = '2.0.0';

if (PHP_VERSION_ID < 80100) {
    throw new RuntimeException(
        'NileAndSinai Connector requires PHP 8.1 or newer.'
    );
}

final class NileAndSinaiBootstrap
{
    private static bool $loaded = false;
    private static bool $booted = false;
    private static array $options = [];

    public static function load(): void
    {
        if (self::$loaded) {
            return;
        }

        $base = __DIR__;

        /*
        * connector.php defines OTAEnv.
        * Load it first so the entire Connector stack has access to
        * server-side configuration immediately after bootstrap.
        */
        $connectorFile = $base . '/connector.php';

        if (!is_file($connectorFile)) {
            throw new RuntimeException(
                'Connector core missing: ' . $connectorFile
            );
        }

        require_once $connectorFile;

        /*
        * Load the Connector environment immediately.
        *
        * This MUST happen before loading modules that depend on
        * configuration such as security, sessions, cache, JWT,
        * logging and database services.
        */
        $envFile = $base . DIRECTORY_SEPARATOR . '.env';

        if (!is_file($envFile)) {
            throw new RuntimeException(
                'Connector environment file missing: ' . $envFile
            );
        }

        if (!is_readable($envFile)) {
            throw new RuntimeException(
                'Connector environment file is not readable: ' . $envFile
            );
        }

        OTAEnv::load($envFile);

        $files = [

            $base . '/Auth/Jwt.php',
            $base . '/Auth/Permissions.php',
            $base . '/Auth/Session.php',
            $base . '/Auth/Token.php',

            $base . '/Database/Database.php',
            $base . '/Database/ConnectionPool.php',
            $base . '/Database/QueryBuilder.php',

            $base . '/Helpers/Response.php',
            $base . '/Helpers/Sanitizer.php',
            $base . '/Helpers/Utilities.php',
            $base . '/Helpers/Validator.php',

            $base . '/Logger/LogTypes.php',
            $base . '/Logger/oLogger.php',

            $base . '/Security/Headers.php',
            $base . '/Security/OriginValidator.php',
            $base . '/Security/RateLimiter.php',
            $base . '/Security/RequestValidator.php',
            $base . '/Security/DeviceFingerprint.php',
            $base . '/Security/Csrf.php',
            $base . '/Security/RequestContext.php',
            $base . '/Security/Security.php',

            $base . '/Exceptions/AuthenticationException.php',
            $base . '/Exceptions/AuthorizationException.php',
            $base . '/Exceptions/ValidationException.php',
            $base . '/Exceptions/RateLimitException.php',
            $base . '/Exceptions/SecurityException.php',

            $base . '/Services/ConfigService.php',
            $base . '/Services/HealthService.php',
            $base . '/Services/CacheService.php',
            $base . '/Services/ApiExceptionHandler.php',
        ];

        foreach ($files as $file) {
            if (!is_file($file)) {
                throw new RuntimeException(
                    'Connector bootstrap dependency missing: ' . $file
                );
            }

            require_once $file;
        }

        self::$loaded = true;
    }

    public static function boot(array $options = []): array
    {
        self::load();

        if (self::$booted) {
            return self::status();
        }

        self::$options = array_merge([
            'security' => true,
            'csp' => true,
            'session' => false,
            'csrf' => false,
            'json' => false,
            'methods' => null,
            'payload_limit' => null,
            'rate_limit' => null,
            'exception_handler' => true,
        ], $options);

        RequestContext::init();

        if ((bool) self::$options['exception_handler']) {
            ApiExceptionHandler::register();
        }

        if ((bool) self::$options['security']) {
            Security::init(
                (bool) self::$options['csp'],
                self::$options['csp_nonce'] ?? null
            );
        }

        if ((bool) self::$options['session']) {
            Session::start();
        }

        if (is_array(self::$options['methods']) && self::$options['methods'] !== []) {
            RequestValidator::ensureMethod(self::$options['methods']);
        }

        if ((bool) self::$options['json']) {
            RequestValidator::ensureJsonRequest();
        }

        if (self::$options['payload_limit'] !== null) {
            RequestValidator::payloadSizeLimit(
                (int) self::$options['payload_limit']
            );
        }

        if ((bool) self::$options['csrf']) {
            if (!(bool) self::$options['session']) {
                throw new RuntimeException(
                    'CSRF protection requires session => true.'
                );
            }

            $method = strtoupper(
                (string) ($_SERVER['REQUEST_METHOD'] ?? 'GET')
            );

            if (in_array($method, ['POST', 'PUT', 'PATCH', 'DELETE'], true)) {
                Csrf::assertValid();
            }
        }

        $rate = self::$options['rate_limit'];

        if (is_array($rate) && isset($rate['key'])) {
            $result = RateLimiter::hit(
                (string) $rate['key'],
                (int) ($rate['limit'] ?? 60),
                (int) ($rate['window'] ?? 60)
            );

            if (!($result['allowed'] ?? false)) {
                throw new RateLimitException(
                    'Too many requests.',
                    $result
                );
            }
        }

        self::$booted = true;

        return self::status();
    }

    public static function db(): PDO
    {
        self::load();
        return OTADatabaseFacade::pdo();
    }

    public static function status(): array
    {
        self::load();

        return [
            'bootstrap' => [
                'name' => 'NileAndSinai Connector Bootstrap',
                'version' => NSA_BOOTSTRAP_VERSION,
                'loaded' => self::$loaded,
                'booted' => self::$booted,
            ],
            'connector' => [
                'version' => defined('OTA_CONNECTOR_VERSION')
                    ? OTA_CONNECTOR_VERSION
                    : 'unknown',
                'system_version' => defined('OTA_SYSTEM_VERSION')
                    ? OTA_SYSTEM_VERSION
                    : 'unknown',
                'build' => defined('OTA_CONNECTOR_BUILD')
                    ? OTA_CONNECTOR_BUILD
                    : 'unknown',
            ],
            'runtime' => [
                'php' => PHP_VERSION,
                'sapi' => PHP_SAPI,
                'request_id' => class_exists('RequestContext')
                    ? RequestContext::id()
                    : null,
                'https' => class_exists('OTASecurity')
                    ? OTASecurity::isHttps()
                    : false,
                'session_active' => session_status() === PHP_SESSION_ACTIVE,
            ],
            'options' => self::$options,
        ];
    }

    public static function reset(): void
    {
        self::$booted = false;
        self::$options = [];
    }
}

NileAndSinaiBootstrap::load();

function nsa_bootstrap(array $options = []): array
{
    return NileAndSinaiBootstrap::boot($options);
}

function nsa_db(): PDO
{
    return NileAndSinaiBootstrap::db();
}

function nsa_config(string $key, mixed $default = null): mixed
{
    return ConfigService::get($key, $default);
}

function nsa_rate_limit(
    string $key,
    int $limit = 60,
    int $windowSeconds = 60
): array {
    return RateLimiter::hit($key, $limit, $windowSeconds);
}

function nsa_request_id(): string
{
    return RequestContext::id();
}

function nsa_json_body(): array
{
    $raw = PHP_SAPI === 'cli'
        ? trim((string) stream_get_contents(STDIN))
        : (string) file_get_contents('php://input');

    if (trim($raw) === '') {
        return [];
    }

    try {
        $data = json_decode(
            $raw,
            true,
            512,
            JSON_THROW_ON_ERROR | JSON_INVALID_UTF8_SUBSTITUTE
        );
    } catch (JsonException $e) {
        throw new ValidationException(
            'Invalid JSON request body.',
            ['json' => 'Malformed JSON.'],
            422,
            $e
        );
    }

    if (!is_array($data)) {
        throw new ValidationException(
            'Invalid JSON request body.',
            ['json' => 'JSON must decode to an object or array.']
        );
    }

    return $data;
}

function nsa_bootstrap_status(): array
{
    return NileAndSinaiBootstrap::status();
}

function nsa_bootstrap_reset(): void
{
    NileAndSinaiBootstrap::reset();
}

function nsa_log_event(
    string $type,
    string $status,
    string $message,
    array $details = [],
    ?PDO $pdo = null,
    string $source = LogTypes::SOURCE_API,
    ?string $niceMessage = null,
    ?int $userId = null,
    ?string $sessionId = null
): bool {
    return OTALogger::log(
        $type,
        $status,
        $message,
        $details,
        $pdo,
        $source,
        $niceMessage,
        $userId,
        $sessionId
    );
}