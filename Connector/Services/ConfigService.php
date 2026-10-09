<?php
declare(strict_types=1);

require_once dirname(__DIR__) . '/connector.php';

final class ConfigService
{
    public static function get(string $key, mixed $default = null): mixed
    {
        $value = OTAEnv::get($key, is_string($default) ? $default : null);
        return $value ?? $default;
    }

    public static function version(): string
    {
        return OTA_CONNECTOR_VERSION;
    }

    public static function appName(): string
    {
        return (string) OTAEnv::get('APP_NAME', 'OnTrackAssets');
    }
}
