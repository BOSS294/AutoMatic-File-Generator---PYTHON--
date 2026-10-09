<?php
declare(strict_types=1);

require_once dirname(__DIR__) . '/connector.php';

/**
 * NileAndSinai V2 - Origin Validator
 * Version: 2.0.0
 *
 * Production policy:
 *   - Local/development environments may operate without configured origins.
 *   - Production requires ALLOWED_ORIGINS for protected browser requests.
 *
 * Non-browser requests that provide no Origin header are allowed because
 * Origin is not universally sent by API clients.
 */

final class OriginValidator
{
    public static function allowed(): array
    {
        return OTASecurity::allowedOrigins();
    }

    public static function isAllowed(?string $origin): bool
    {
        $origin = trim((string) $origin);

        if ($origin === '') {
            return true;
        }

        $allowed = self::allowed();

        /*
         * Do not allow browser-origin requests through an empty production
         * allowlist.
         */
        if ($allowed === []) {
            $env = strtolower((string) OTAEnv::get('APP_ENV', 'production'));

            return in_array($env, ['local', 'development', 'dev', 'testing'], true);
        }

        foreach ($allowed as $allowedOrigin) {
            if (OTASecurity::originMatches($origin, $allowedOrigin)) {
                return true;
            }
        }

        return false;
    }

    public static function assertAllowed(?string $origin = null): void
    {
        $origin ??= (string) ($_SERVER['HTTP_ORIGIN'] ?? '');

        if (!self::isAllowed($origin)) {
            throw new RuntimeException('Origin not allowed.');
        }
    }

    public static function assertConfiguredForProduction(): void
    {
        $env = strtolower((string) OTAEnv::get('APP_ENV', 'production'));

        if (!in_array($env, ['production', 'prod'], true)) {
            return;
        }

        if (self::allowed() === []) {
            throw new RuntimeException(
                'ALLOWED_ORIGINS must be configured in production.'
            );
        }
    }
}