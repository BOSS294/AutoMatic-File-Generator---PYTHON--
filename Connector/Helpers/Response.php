<?php
declare(strict_types=1);

require_once dirname(__DIR__) . '/connector.php';

final class Response
{
    public static function json(array $data, int $status = 200): never
    {
        ota_json_response($data, $status);
    }

    public static function success(string $message, array $data = [], int $status = 200): never
    {
        self::json([
            'success' => true,
            'message' => $message,
            'data' => $data,
            'version' => OTA_CONNECTOR_VERSION,
        ], $status);
    }

    public static function error(string $message, int $status = 400, array $data = []): never
    {
        self::json([
            'success' => false,
            'message' => $message,
            'data' => $data,
            'version' => OTA_CONNECTOR_VERSION,
        ], $status);
    }
}
