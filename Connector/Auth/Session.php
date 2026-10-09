<?php
declare(strict_types=1);

require_once dirname(__DIR__) . '/connector.php';

final class Session
{
    public static function start(): void
    {
        if (PHP_SAPI === 'cli') {
            return;
        }

        if (session_status() === PHP_SESSION_NONE) {
            $name = (string) OTAEnv::get('SESSION_NAME', 'OTA_SESSION');
            session_name($name);
            session_start([
                'cookie_httponly' => true,
                'cookie_secure' => OTASecurity::isHttps(),
                'cookie_samesite' => 'Strict',
                'use_strict_mode' => true,
                'use_only_cookies' => true,
            ]);
        }
    }

    public static function regenerate(): void
    {
        self::start();
        if (session_status() === PHP_SESSION_ACTIVE) {
            session_regenerate_id(true);
        }
    }

    public static function set(string $key, mixed $value): void
    {
        self::start();
        $_SESSION[$key] = $value;
    }

    public static function get(string $key, mixed $default = null): mixed
    {
        self::start();
        return $_SESSION[$key] ?? $default;
    }

    public static function remove(string $key): void
    {
        self::start();
        unset($_SESSION[$key]);
    }

    public static function destroy(): void
    {
        self::start();
        $_SESSION = [];
        if (session_status() === PHP_SESSION_ACTIVE) {
            session_destroy();
        }
    }
}
