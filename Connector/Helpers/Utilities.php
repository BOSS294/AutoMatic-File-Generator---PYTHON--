<?php
declare(strict_types=1);

require_once dirname(__DIR__) . '/connector.php';

final class Utilities
{
    public static function env(string $key, mixed $default = null): mixed
    {
        return OTAEnv::get($key, is_string($default) ? $default : null) ?? $default;
    }

    public static function db(): PDO
    {
        return ota_db();
    }

    public static function version(): string
    {
        return OTA_CONNECTOR_VERSION;
    }

    public static function nowIso(): string
    {
        return gmdate('c');
    }

    public static function mask(string $value, int $visible = 3): string
    {
        return ota_mask_string($value, $visible);
    }

    public static function clientIp(): string
    {
        return OTASecurity::clientIp();
    }
}
