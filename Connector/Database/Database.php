<?php
declare(strict_types=1);

require_once dirname(__DIR__) . '/connector.php';

final class OTAConnectionPool
{
    /** @var array<string, PDO> */
    private static array $pool = [];

    public static function get(?string $key = null): PDO
    {
        $key ??= 'default';
        if (!isset(self::$pool[$key])) {
            self::$pool[$key] = ota_db();
        }
        return self::$pool[$key];
    }

    public static function put(string $key, PDO $pdo): void
    {
        self::$pool[$key] = $pdo;
    }

    public static function reset(?string $key = null): void
    {
        if ($key === null) {
            self::$pool = [];
            OTADatabase::reset();
            return;
        }

        unset(self::$pool[$key]);
    }

    public static function ping(?string $key = null): array
    {
        return ping_connection(self::get($key));
    }
}

final class OTADatabaseFacade
{
    public static function pdo(): PDO
    {
        return OTAConnectionPool::get();
    }

    public static function ping(): array
    {
        return OTAConnectionPool::ping();
    }

    public static function prepare(string $sql): PDOStatement
    {
        return self::pdo()->prepare($sql);
    }

    public static function query(string $sql): PDOStatement
    {
        return self::pdo()->query($sql);
    }
}
