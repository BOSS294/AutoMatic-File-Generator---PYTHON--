<?php
declare(strict_types=1);

/**
 * NileAndSinai V2 - Request Context
 * Version: 1.0.0
 *
 * Correlation/request identity used by HTTP responses and logging.
 */

final class RequestContext
{
    private static ?string $id = null;
    private static float $startedAt = 0.0;

    public static function init(): string
    {
        if (self::$id !== null) {
            return self::$id;
        }

        self::$startedAt = microtime(true);

        $incoming = trim((string) ($_SERVER['HTTP_X_REQUEST_ID'] ?? ''));

        if (
            $incoming !== ''
            && strlen($incoming) <= 128
            && preg_match('/^[A-Za-z0-9._:-]+$/', $incoming)
        ) {
            self::$id = $incoming;
        } else {
            self::$id = bin2hex(random_bytes(16));
        }

        if (PHP_SAPI !== 'cli' && !headers_sent()) {
            header('X-Request-ID: ' . self::$id);
        }

        return self::$id;
    }

    public static function id(): string
    {
        return self::init();
    }

    public static function elapsedMs(): int
    {
        if (self::$startedAt <= 0) {
            self::init();
        }

        return (int) round((microtime(true) - self::$startedAt) * 1000);
    }
}