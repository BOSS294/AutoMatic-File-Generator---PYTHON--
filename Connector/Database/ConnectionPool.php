<?php
declare(strict_types=1);

require_once __DIR__ . '/Database.php';

final class ConnectionPool
{
    public static function get(string $name = 'default'): PDO
    {
        return OTAConnectionPool::get($name);
    }

    public static function ping(string $name = 'default'): array
    {
        return OTAConnectionPool::ping($name);
    }

    public static function reset(?string $name = null): void
    {
        OTAConnectionPool::reset($name);
    }
}
