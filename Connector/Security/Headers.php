<?php
declare(strict_types=1);

require_once dirname(__DIR__) . '/connector.php';

/**
 * NileAndSinai V2 - Security Headers
 * Version: 2.0.0
 *
 * Centralizes baseline browser security headers and optional CSP.
 */

final class Headers
{
    public static function apply(): void
    {
        if (PHP_SAPI === 'cli' || headers_sent()) {
            return;
        }

        OTASecurity::applyHeaders();
    }

    public static function applyCsp(?string $nonce = null): void
    {
        if (PHP_SAPI === 'cli' || headers_sent()) {
            return;
        }

        $env = strtolower((string) OTAEnv::get('APP_ENV', 'production'));
        $connect = trim((string) OTAEnv::get('CSP_CONNECT_SRC', "'self'"));

        /*
         * Keep the baseline strict. Inline scripts are disabled unless a
         * server-generated nonce is explicitly supplied.
         */
        $scriptSrc = "'self'";
        if ($nonce !== null && $nonce !== '') {
            $scriptSrc .= " 'nonce-" . self::sanitizeNonce($nonce) . "'";
        }

        $directives = [
            "default-src 'self'",
            "base-uri 'self'",
            "object-src 'none'",
            "frame-ancestors 'self'",
            "form-action 'self'",
            "img-src 'self' data: https:",
            "font-src 'self' data: https:",
            "style-src 'self' 'unsafe-inline' https:",
            "script-src {$scriptSrc}",
            "connect-src {$connect}",
            "media-src 'self' blob: https:",
            "worker-src 'self' blob:",
        ];

        if (in_array($env, ['local', 'development', 'dev'], true)) {
            $directives[] = "upgrade-insecure-requests";
        }

        header('Content-Security-Policy: ' . implode('; ', $directives));
    }

    private static function sanitizeNonce(string $nonce): string
    {
        return preg_replace('/[^A-Za-z0-9+\/=_-]/', '', $nonce) ?? '';
    }
}