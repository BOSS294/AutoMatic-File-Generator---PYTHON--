<?php
declare(strict_types=1);

require_once dirname(__DIR__) . '/connector.php';

/**
 * NileAndSinai V2 - Request Validator
 * Version: 2.0.0
 */

final class RequestValidator
{
    public static function ensureJsonRequest(): void
    {
        if (PHP_SAPI === 'cli') {
            return;
        }

        $contentType = strtolower((string) ($_SERVER['CONTENT_TYPE'] ?? ''));

        if ($contentType === '' || !str_contains($contentType, 'application/json')) {
            throw new RuntimeException('JSON content type required.');
        }
    }

    public static function ensureMethod(array $methods = ['GET', 'POST']): void
    {
        OTASecurity::assertRequestMethod($methods);
    }

    public static function payloadSizeLimit(int $bytes = 1024 * 1024): void
    {
        if ($bytes < 1) {
            throw new InvalidArgumentException('Payload limit must be positive.');
        }

        $len = (int) ($_SERVER['CONTENT_LENGTH'] ?? 0);

        if ($len > $bytes) {
            throw new RuntimeException('Payload too large.');
        }
    }

    public static function requestId(): string
    {
        return RequestContext::id();
    }

    public static function clientIp(): string
    {
        return OTASecurity::clientIp();
    }
}