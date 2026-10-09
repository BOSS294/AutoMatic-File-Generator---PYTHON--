<?php
declare(strict_types=1);

require_once dirname(__DIR__) . '/connector.php';

final class HealthService
{
    public static function ping(?PDO $pdo = null): array
    {
        return ping_connection($pdo);
    }

    public static function status(): array
    {
        try {
            $ping = self::ping();
            return [
                'healthy' => (bool)($ping['success'] ?? false),
                'version' => OTA_CONNECTOR_VERSION,
                'details' => $ping,
            ];
        } catch (Throwable $e) {
            return [
                'healthy' => false,
                'version' => OTA_CONNECTOR_VERSION,
                'error' => $e->getMessage(),
            ];
        }
    }
}
