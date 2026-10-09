<?php
declare(strict_types=1);

require_once dirname(__DIR__) . '/connector.php';

final class CacheService
{
    private static function path(string $key): string
    {
        $prefix = (string) OTAEnv::get('CACHE_PREFIX', 'ota');
        return sys_get_temp_dir() . DIRECTORY_SEPARATOR . $prefix . '_' . sha1($key) . '.cache';
    }

    public static function set(string $key, mixed $value, int $ttlSeconds = 300): bool
    {
        $payload = [
            'expires_at' => time() + $ttlSeconds,
            'value' => $value,
        ];
        return file_put_contents(self::path($key), serialize($payload)) !== false;
    }

    public static function get(string $key, mixed $default = null): mixed
    {
        $file = self::path($key);
        if (!is_file($file)) {
            return $default;
        }

        $raw = file_get_contents($file);
        if ($raw === false) {
            return $default;
        }

        $payload = @unserialize($raw);
        if (!is_array($payload) || ($payload['expires_at'] ?? 0) < time()) {
            @unlink($file);
            return $default;
        }

        return $payload['value'] ?? $default;
    }

    public static function delete(string $key): bool
    {
        $file = self::path($key);
        return !is_file($file) || @unlink($file);
    }

    public static function remember(string $key, int $ttlSeconds, callable $callback): mixed
    {
        $existing = self::get($key, null);
        if ($existing !== null) {
            return $existing;
        }

        $value = $callback();
        self::set($key, $value, $ttlSeconds);
        return $value;
    }
}
